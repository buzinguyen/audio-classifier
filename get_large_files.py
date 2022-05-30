import wget
import os

wget.download("https://storage.googleapis.com/audioset/vggish_pca_params.npz", "./assets/vggish_pca_params.npz")
wget.download("https://storage.googleapis.com/audioset/vggish_model.ckpt", "./assets/vggish_model.ckpt")
os.system("wget --no-check-certificate 'https://docs.google.com/uc?export=download&id=1nHfCiklLEzlcAuW9zAW38dRkaTCjicjo' -O './assets/classifier_model.h5'")