# `GazeReg` data collection application and evaluation service
This repository contains the full code for the data collection application developed as part of the thesis for collecting
multi-screen gaze data. Furthermore, it contains the code for the evaluation service.

## Structure
`src/conf` contains session configurations as JSON documents.<br>
`src/static` contains the code for the Frontend component.<br>
`src/templates` contains the HTML page for the Frontend component.<br>
`src/tools` contains the toolchain used for evaluation, training, etc. This is not part of the thesis and is only supplied for methodical clarity.<br>

## Setup
Create a virtual environment (Python 3.11.x) and install the packages listed in `requirements.txt`.

## Starting the data collection application
To start the service, export the `DATACOLL_USED_CERT`, `DATACOLL_USED_KEY`, and `DATACOLL_USED_REGION_CONFIG` environment variables. To
generate a certificate and key pair, you can use `mkcert`.
Then, start the app using the following command (Linux):
```bash
DATACOLL_USED_REGION_CONFIG="src/conf/mtmsession.json" DATACOLL_USED_CERT="..." DATACOLL_USED_KEY="..." python src/app.py
```
A command for Windows can be found in `src/app.py`.

## Starting the evaluation service
To start the evaluation service, use the following command (Linux):
```bash
GAZEREG_CERT_FILE="..." GAZEREG_KEY_FILE="..." python src/clssrv.py
```