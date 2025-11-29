# Note
This is a fork of [this](https://github.com/g0t4/zed-zeta-server) I take no credit, the only changes I made were styling/cleanup.

## Running server

```bash
# create venv (pick one):
uv venv

source venv/bin/activate
uv pip install -r requirements.txt

./run.sh
```

## Serving the model (llama.cpp)
Run using a 22GB 2080 Ti, Zeds edit feature seems to take longer depending on how "satisfying" a result it gets from the LLM
```sh
$LLM_DIR/llama-server -hf bartowski/zed-industries_zeta-GGUF:Q6_K_L \
--host 0.0.0.0 \
--port 10002 \
--gpu-layers 999 \
--cont-batching \
--flash-attn on \
--parallel 1 \
--threads 4 \
--cache-type-k f16 \
--cache-type-v f16 \
--no-mmproj \
-a "zeta" \
--ctx-size 4096 \
--batch-size 2048 \
--ubatch-size 256 \
--jinja 
```

## Using Zed
Port is the port of this proxy server not the LLM
```sh
export ZED_PREDICT_EDITS_URL=http://localhost:port/predict_edits
zed
```
On Windows you would add this as a System or User environment variable. Make sure to use the devices IP instead of localhost if you arent running the model on the same machine.
