"""Reproducible image preprocessing review for KU39.

The split generated here is NEW preparation evidence. It is not the original
training split and must not be used to validate the already trained website model.
"""
from pathlib import Path
from collections import Counter
import hashlib, io, json, zipfile
import numpy as np
import pandas as pd
from PIL import Image, ImageOps, ImageEnhance
import matplotlib.pyplot as plt
from sklearn.model_selection import StratifiedGroupKFold

CLASSES = ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy']
SEED = 39

def paths(root):
    root = Path(root)
    out = root/'results'/'outputs'
    figures = root/'results'/'eda_visualizations'
    out.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    return root/'data'/'raw'/'archive.zip', out, figures

def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1024*1024), b''): h.update(b)
    return h.hexdigest()

def audit(root, force=False):
    """Decode every image and cache only against an identical source archive hash."""
    archive, out, _ = paths(root)
    if not archive.exists():
        raise FileNotFoundError(f'Put the supplied dataset ZIP at {archive}')
    signature = sha_file(archive)
    cache = out/'audit_manifest.csv'
    marker = out/'audit_source.json'
    if not force and cache.exists() and marker.exists():
        if json.loads(marker.read_text()).get('archive_sha256') == signature:
            return pd.read_csv(cache, keep_default_na=False)
    rows = []
    with zipfile.ZipFile(archive) as z:
        names = sorted(n for n in z.namelist()
                       if not n.endswith('/') and Path(n).suffix.lower() in {'.jpg','.jpeg','.png'})
        for name in names:
            b = z.read(name)
            label = Path(name).parent.name
            row = dict(path=name, label=label, bytes=len(b),
                       file_sha256=hashlib.sha256(b).hexdigest(), valid=False,
                       error='', width=0, height=0, mode='', image_format='',
                       rgb_sha256='', mean_brightness=np.nan, contrast=np.nan)
            try:
                if label not in CLASSES: raise ValueError('Unknown class label')
                with Image.open(io.BytesIO(b)) as im:
                    im.load()
                    row.update(width=im.width, height=im.height, mode=im.mode, image_format=im.format)
                    rgb = ImageOps.exif_transpose(im).convert('RGB')
                    # Include dimensions to distinguish different spatial arrays.
                    row['rgb_sha256'] = hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()
                    gray = np.asarray(rgb.resize((64,64)).convert('L'), dtype=np.float32)
                    row.update(valid=True, mean_brightness=float(gray.mean()), contrast=float(gray.std()))
            except Exception as e:
                row['error'] = type(e).__name__+': '+str(e)
            rows.append(row)
    frame = pd.DataFrame(rows)
    frame.to_csv(cache, index=False)
    frame.loc[~frame.valid].to_csv(out/'corrupt_or_unknown_label_exclusions.csv', index=False)
    marker.write_text(json.dumps({'archive_sha256':signature,'image_entries':len(frame),
        'method':'Full decode; exact file hash; exact oriented RGB pixel hash; brightness on 64x64 grayscale'},indent=2))
    return frame

def clean_and_split(frame, root):
    """Exclude invalid/conflicting labels; keep one of each exact pixel duplicate group."""
    _, out, _ = paths(root)
    valid = frame.loc[frame.valid == True].copy()
    conflicts = valid.groupby('rgb_sha256').label.nunique()
    conflict_hashes = set(conflicts[conflicts > 1].index)
    conflict_rows = valid[valid.rgb_sha256.isin(conflict_hashes)]
    consistent = valid[~valid.rgb_sha256.isin(conflict_hashes)].sort_values('path')
    duplicate_rows = consistent[consistent.duplicated('rgb_sha256',keep='first')]
    cleaned = consistent.drop_duplicates('rgb_sha256',keep='first').copy().reset_index(drop=True)
    cleaned['label_id'] = cleaned.label.map({c:i for i,c in enumerate(CLASSES)})
    if cleaned.groupby('label').size().min() < 5:
        raise ValueError('Need at least five retained examples per class for this five-fold partition.')
    splitter = StratifiedGroupKFold(n_splits=5,shuffle=True,random_state=SEED)
    cleaned['preparation_fold'] = -1
    for fold, (_, held) in enumerate(splitter.split(cleaned,cleaned.label_id,groups=cleaned.rgb_sha256)):
        cleaned.loc[held,'preparation_fold'] = fold
    cleaned['preparation_split'] = cleaned.preparation_fold.map({0:'test',1:'validation',2:'train',3:'train',4:'train'})
    groups = {s:set(cleaned.loc[cleaned.preparation_split==s,'rgb_sha256']) for s in ['train','validation','test']}
    assert not groups['train'] & groups['test']
    assert not groups['train'] & groups['validation']
    assert not groups['validation'] & groups['test']
    assert cleaned.preparation_fold.ge(0).all()
    cleaned.to_csv(out/'NEW_preparation_split_manifest.csv',index=False)
    duplicate_rows.to_csv(out/'exact_pixel_duplicate_exclusions.csv',index=False)
    conflict_rows.to_csv(out/'conflicting_label_exclusions.csv',index=False)
    (out/'class_mapping.json').write_text(json.dumps({c:i for i,c in enumerate(CLASSES)},indent=2))
    return cleaned, duplicate_rows, conflict_rows

def load_image(root, archive_path):
    archive,_,_=paths(root)
    with zipfile.ZipFile(archive) as z:
        with Image.open(io.BytesIO(z.read(archive_path))) as im:
            im.load()
            return ImageOps.exif_transpose(im).convert('RGB')

def prepare_image(image):
    return np.asarray(image.resize((224,224),Image.Resampling.BILINEAR),dtype=np.float32)

def finish(fig,root,name):
    _,_,figures=paths(root)
    fig.tight_layout()
    fig.savefig(figures/name,dpi=130,bbox_inches='tight')
    from IPython.display import display
    display(fig)
    plt.close(fig)
    return figures/name

def integrity_plot(frame,root):
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    counts=frame.groupby('label').size().reindex(CLASSES,fill_value=0)
    counts.plot.bar(ax=axes[0],color='#26856c',rot=20)
    axes[0].set(title='Raw archive image entries',ylabel='Images',xlabel='Class')
    for i,v in enumerate(counts): axes[0].text(i,v,str(v),ha='center',va='bottom')
    good=frame[frame.valid==True]
    axes[1].scatter(good.width,good.height,s=10,alpha=.25,color='#305b94')
    axes[1].set(title='Decoded image dimensions',xlabel='Width (pixels)',ylabel='Height (pixels)')
    return finish(fig,root,'01_integrity_and_dimensions.png')

def split_plot(cleaned,root):
    table=pd.crosstab(cleaned.label,cleaned.preparation_split).reindex(CLASSES).reindex(columns=['train','validation','test'])
    fig,ax=plt.subplots(figsize=(9,4))
    table.plot.bar(ax=ax,rot=15,color=['#26856c','#d6a24d','#305b94'])
    ax.set(title='NEW preparation split after exact duplicate cleaning',ylabel='Images',xlabel='Class')
    return finish(fig,root,'02_NEW_preparation_split.png')

def resize_plot(frame,root):
    selected=frame[frame.valid==True].sort_values('path').groupby('label').head(1)
    fig,axes=plt.subplots(2,4,figsize=(12,6))
    for j,c in enumerate(CLASSES):
        row=selected[selected.label==c].iloc[0];im=load_image(root,row.path)
        axes[0,j].imshow(im);axes[0,j].set_title(f'{c}\n{im.width}x{im.height}')
        axes[1,j].imshow(prepare_image(im).astype('uint8'));axes[1,j].set_title('RGB 224x224')
        axes[0,j].axis('off');axes[1,j].axis('off')
    return finish(fig,root,'03_rgb_resize_examples.png')

def label_plot(cleaned,root):
    train=cleaned[cleaned.preparation_split=='train']
    counts=train.groupby('label').size().reindex(CLASSES)
    fig,ax=plt.subplots(figsize=(8,4))
    counts.plot.bar(ax=ax,rot=15,color='#26856c')
    ax.set(title='Class balance in NEW preparation training split',ylabel='Images',xlabel='Class')
    return finish(fig,root,'04_training_class_balance.png')

def normalization_plot(cleaned,root):
    train=cleaned[cleaned.preparation_split=='train']
    im=load_image(root,train.sort_values('path').iloc[0].path)
    x=prepare_image(im)
    arrays=[x,x/255.0,x/127.5-1.0]
    titles=['EfficientNet input: 0–255 (scaling inside model)', 'Custom CNN option: 0–1', 'MobileNetV2 option: −1–1']
    fig,axes=plt.subplots(1,3,figsize=(13,3.8))
    for ax,a,t in zip(axes,arrays,titles):
        ax.hist(a.ravel(),bins=40,color='#305b94');ax.set(title=t,xlabel='Value',ylabel='Channel values')
    return finish(fig,root,'05_model_input_ranges.png')

def augment(image,seed=SEED):
    rng=np.random.default_rng(seed)
    return ImageEnhance.Brightness(image.transpose(Image.Transpose.FLIP_LEFT_RIGHT).rotate(float(rng.uniform(-12,12)),resample=Image.Resampling.BILINEAR)).enhance(float(rng.uniform(.85,1.15)))

def augmentation_plot(cleaned,root):
    train=cleaned[cleaned.preparation_split=='train']
    fig,axes=plt.subplots(3,4,figsize=(12,8))
    measurements=[]
    for j,c in enumerate(CLASSES):
        row=train[train.label==c].sort_values('path').iloc[0]
        im=load_image(root,row.path).resize((224,224),Image.Resampling.BILINEAR)
        flipped=im.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        changed=augment(im,SEED+j)
        for i,(title,v) in enumerate([('Original',im),('Horizontal flip',flipped),('Flip + rotation + brightness',changed)]):
            axes[i,j].imshow(v);axes[i,j].axis('off');axes[i,j].set_title(f'{c}\n{title}',fontsize=10)
            measurements.append({'label':c,'variant':title,'mean_brightness':float(np.asarray(v).mean()),'source_split':'train','source_path':row.path})
    _,out,_=paths(root);pd.DataFrame(measurements).to_csv(out/'augmentation_demo_measurements.csv',index=False)
    return finish(fig,root,'06_training_only_augmentation.png')
