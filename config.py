import os
import sys

JSON_AS_ASCII = False

MAX_CONTENT_LENGTH = 5242880

# Flask debug mode
DEBUG = False

# Server port
PORT = 23456

# Absolute path of vits-simple-api
ABS_PATH = os.path.dirname(os.path.realpath(__file__))

# Upload path
UPLOAD_FOLDER = ABS_PATH + "/upload"

# Cahce path
CACHE_PATH = ABS_PATH + "/cache"

# Logs path
LOGS_PATH = ABS_PATH + "/logs"

# Set the number of backup log files to keep. 
LOGS_BACKUPCOUNT = 30

# If CLEAN_INTERVAL_SECONDS <= 0, the cleaning task will not be executed.
CLEAN_INTERVAL_SECONDS = 3600

# save audio to CACHE_PATH
SAVE_AUDIO = False

# zh ja ko en... If it is empty, it will be read based on the text_cleaners specified in the config.json.
LANGUAGE_AUTOMATIC_DETECT = []

# Set to True to enable API Key authentication
API_KEY_ENABLED = False

# API_KEY is required for authentication
API_KEY = "api-key"

# logging_level:DEBUG/INFO/WARNING/ERROR/CRITICAL
LOGGING_LEVEL = "DEBUG"

# Language identification library. Optional fastlid, langid
LANGUAGE_IDENTIFICATION_LIBRARY = "fastlid"

# To use the english_cleaner, you need to install espeak and provide the path of libespeak-ng.dll as input here.
# If ESPEAK_LIBRARY is set to empty, it will be read from the environment variable.
# For windows : "C:/Program Files/eSpeak NG/libespeak-ng.dll"
ESPEAK_LIBRARY = ""

# Fill in the model path here
MODEL_LIST = [
    # VITS
    [ABS_PATH + "/Model/Nene_Nanami_Rong_Tang/1374_epochs.pth", ABS_PATH + "/Model/Nene_Nanami_Rong_Tang/config.json"],
    [ABS_PATH + "/Model/Zero_no_tsukaima/1158_epochs.pth", ABS_PATH + "/Model/Zero_no_tsukaima/config.json"],
    [ABS_PATH + "/Model/vits-uma-genshin-honkai/G_953000.pth", ABS_PATH + "/Model/vits-uma-genshin-honkai/config.json"],
    
    # HuBert-VITS (Need to configure HUBERT_SOFT_MODEL)
    [ABS_PATH + "/Model/louise/360_epochs.pth", ABS_PATH + "/Model/louise/config.json"],
    
    # W2V2-VITS (Need to configure DIMENSIONAL_EMOTION_NPY)
    # [ABS_PATH + "/Model/w2v2-vits/1026_epochs.pth", ABS_PATH + "/Model/w2v2-vits/config.json"],
    
    # Bert-VITS2
    [ABS_PATH + "/bert_vits2/Model/suansuanpro/naxida/G_5100.pth", ABS_PATH + "/bert_vits2/Model/suansuanpro/naxida/config.json"],
    [ABS_PATH + "/bert_vits2/Model/suansuanpro/kq_kl/G_5900.pth", ABS_PATH + "/bert_vits2/Model/suansuanpro/kq_kl/config.json"],
    [ABS_PATH + "/bert_vits2/Model/suansuanpro/paim/G_1900.pth", ABS_PATH + "/bert_vits2/Model/suansuanpro/paim/config.json"],
    [ABS_PATH + "/bert_vits2/Model/suansuanpro/sllh-z/G_4400.pth", ABS_PATH + "/bert_vits2/Model/suansuanpro/sllh-z/config.json"],
    [ABS_PATH + "/bert_vits2/Model/suansuanpro/sllr/G_5400.pth", ABS_PATH + "/bert_vits2/Model/suansuanpro/sllr/config.json"],
    [ABS_PATH + "/bert_vits2/Model/suansuanpro/zl/G_4900.pth", ABS_PATH + "/bert_vits2/Model/suansuanpro/zl/config.json"],
    [ABS_PATH + "/bert_vits2/Model/digitalxingtong/Luming/luming.pth", ABS_PATH + "/bert_vits2/Model/digitalxingtong/Luming/config.json"],
    [ABS_PATH + "/bert_vits2/Model/digitalxingtong/Jiaran/jiaran_new.pth", ABS_PATH + "/bert_vits2/Model/digitalxingtong/Jiaran/config.json"],
]

# hubert-vits: hubert soft model
HUBERT_SOFT_MODEL = ABS_PATH + "/Model/hubert-soft-0d54a1f4.pt"

# w2v2-vits: Dimensional emotion npy file
# load single npy: ABS_PATH+"/all_emotions.npy
# load mutiple npy: [ABS_PATH + "/emotions1.npy", ABS_PATH + "/emotions2.npy"]
# load mutiple npy from folder: ABS_PATH + "/Model/npy"
DIMENSIONAL_EMOTION_NPY = ABS_PATH + "/Model/npy"

# w2v2-vits: Need to have both `model.onnx` and `model.yaml` files in the same path.
DIMENSIONAL_EMOTION_MODEL = ABS_PATH + "/Model/model.yaml"

"""
Default parameter
"""

ID = 0

FORMAT = "wav"

LANG = "AUTO"

LENGTH = 1

NOISE = 0.33

NOISEW = 0.4

# 长文本分段阈值，max<=0表示不分段.
# Batch processing threshold. Text will not be processed in batches if max<=0
MAX = 50

# Bert_VITS2
SDP_RATIO = 0.2
