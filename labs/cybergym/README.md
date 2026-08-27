# CyberGym 10-task subset

Source: https://github.com/cybergym-iclr26/cybergym

PoC server: `http://127.0.0.1:8666`

## Tasks

arvo:47101, arvo:3938, arvo:24993, arvo:1065, arvo:10400, arvo:368,
oss-fuzz:42535201, oss-fuzz:42535468, oss-fuzz:370689421, oss-fuzz:385167047

## Start the PoC server

Follow their README subset path. Do not download the 10TB full server.

```bash
pip3 install -e '.[server]'
python scripts/server_data/download_subset.py
wget https://huggingface.co/datasets/cybergym-iclr26/cybergym-server/resolve/main/cybergym-oss-fuzz-data-subset.7z
7z x cybergym-oss-fuzz-data-subset.7z

PORT=8666
POC_SAVE_DIR=./server_poc
CYBERGYM_SERVER_DATA_DIR=./oss-fuzz-data
python3 -m cybergym.server \
    --host 127.0.0.1 --port $PORT \
    --log_dir $POC_SAVE_DIR --db_path $POC_SAVE_DIR/poc.db \
    --cybergym_oss_fuzz_path $CYBERGYM_SERVER_DATA_DIR
```

## Score

```bash
python3 tools/case/lanbb.py case score cybergym
```

n/N is what the PoC server accepts. Quote the server fail text if it rejects.
