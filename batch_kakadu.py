import argparse
import numpy as np
import os
import pandas as pd
import cv2
from skimage.measure import compare_ssim
from skimage.measure import compare_psnr

parser = argparse.ArgumentParser(description='total_cr')
parser.add_argument('--y_path',help='path to y dataset', default='measurements/')
parser.add_argument('--orig_path',help='path to orig image dataset', default='orig/')
parser.add_argument('--represent_path',help='path to represent of kakadu', default='represent/')
parser.add_argument('--recon_path',help='path to recon image dataset', default='recon/')
parser.add_argument('--cr',type=int,default=20)
parser.add_argument('--image_format',help='format of the image', default='bmp')
opt = parser.parse_args()

if not os.path.exists('%s' % (opt.represent_path)):
    os.makedirs('%s' % (opt.represent_path))
if not os.path.exists('%s' % (opt.recon_path)):
    os.makedirs('%s' % (opt.recon_path))

def calc_ent(x):
    x_value_list = set([x[i] for i in range(x.shape[0])])
    ent = 0.0
    for x_value in x_value_list:
        p = float(x[x == x_value].shape[0]) / x.shape[0]
        logp = np.log2(p)
        ent -= p * logp
    return ent

num_files = 0
for fn in os.listdir(opt.y_path):
    num_files += 1

y_number = []
total_cr_number = []
bpp_number = []
psnr_number = []
ssim_number = []
for idx in range(num_files):
    locals()['total_cr_'+str(idx)+''] = opt.cr * 8 / calc_ent(np.loadtxt('%s/y_%d.txt' %(opt.y_path,idx),dtype='int'))
    locals()['bpp_'+str(idx)+''] = 8 / locals()['total_cr_'+str(idx)+'']
    os.system('./kdu_compress -i %s/orig_%d.%s -o %s/out_%d.j2c -rate %.5f' %(opt.orig_path,idx,opt.image_format,opt.represent_path,idx,locals()['bpp_'+str(idx)+'']))

    y_number.append(str(idx))
    total_cr_number.append(locals()['total_cr_'+str(idx)+''])
    bpp_number.append(locals()['bpp_'+str(idx)+''])

for idx in range(num_files):
    os.system('./kdu_expand -i %s/out_%d.j2c -o %s/recon_%d.%s' %(opt.represent_path,idx,opt.recon_path,idx,opt.image_format))

for idx in range(num_files):
    locals()['orig_'+str(idx)+''] = cv2.imread('%s/orig_%d.%s' %(opt.orig_path,idx,opt.image_format))
    locals()['recon_'+str(idx)+''] = cv2.imread('%s/recon_%d.%s' %(opt.recon_path,idx,opt.image_format))
    locals()['psnr_'+str(idx)+''] = compare_psnr(locals()['orig_'+str(idx)+''],locals()['recon_'+str(idx)+''])
    locals()['ssim_'+str(idx)+''] = compare_ssim(locals()['orig_'+str(idx)+''],locals()['recon_'+str(idx)+''],multichannel=True)

    psnr_number.append(locals()['psnr_'+str(idx)+''])
    ssim_number.append(locals()['ssim_'+str(idx)+''])

dit = {'y_number':y_number, 'total_cr':total_cr_number,'bpp':bpp_number,'psnr':psnr_number,'ssim':ssim_number}
df = pd.DataFrame(dit)
df.to_csv(r'./JPEG2000_result.csv',columns=['y_number','total_cr','bpp','psnr','ssim'],index=False,sep=',')
