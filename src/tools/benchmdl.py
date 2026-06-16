# Simulate a very avid gaze detection enthusiast.
from sys                import argv
from os                 import walk
from os.path            import join
from requests           import post
from json               import loads
from urllib3            import disable_warnings
from urllib3.exceptions import InsecureRequestWarning
from json               import dump

import numpy as np


class StopException(Exception):
    pass


if __name__ == '__main__':
    addr = argv[1]
    src  = argv[2]

    # Disable warnings due to self-signed certificates.
    disable_warnings(InsecureRequestWarning)

    i = 5000
    ppTimes  = []
    clsTimes = []
    try:
        for root, d, f in walk(src):
            for fi in f:
                # (1) Read file.
                if not fi.endswith('.jpg'):
                    continue
                else:
                    fname = join(root, fi)
                    with open(fname, 'rb') as file:
                        # (2) Request gaze region classification.
                        resp = post(
                            url='https://' + addr + '/api/classify',
                            files={ 'image': file },
                            verify=False
                        )

                    # (3) Parse and display result.
                    resp = loads(resp.text)
                    if 'timings' not in resp:
                        print('error: You must start the classification service in benchmarking mode for this script to work. '
                              + 'Run the classification server with a predefined environment variable named \"GAZEREG_BENCH\" '
                              + 'set to \"True\" and retry.'
                        )

                        exit(1)
                    if resp['predicted_region'] != -1:
                        s = resp['status']
                        r = resp['predicted_region']
                        t = resp['timings']

                        print(f'Request with file \"{fname}\" succeeded. Predicted region is {r}.')

                        ppTimes.append(t[0])
                        clsTimes.append(t[1])
                        
                        i -= 1
                        if i == 0:
                            raise StopException()
                    else:
                        print(f'error: Request with file \"{fname}\" failed. Reason: {resp["status"]}')
    except StopException:
        print('Finished benchmark.')

    # (4) Evaluate statistics.
    with open('benchmark_results.json', 'w') as out:
        ppTimes  = np.array(ppTimes,  dtype=np.float32)
        clsTimes = np.array(clsTimes, dtype=np.float32)

        print(f'Writing results to \"{out.name}\".')
        obj = {
            'n':    len(ppTimes),
            'thru': float(1000.0 / (ppTimes + clsTimes).mean()),

            'preprocessing': {
                'min':  float(ppTimes.min()),
                'max':  float(ppTimes.max()),
                'mean': float(ppTimes.mean()),
                'std':  float(ppTimes.std()),
                'med':  float(np.median(ppTimes)),
                'p99':  float(np.percentile(ppTimes, 99)),
                'p90':  float(np.percentile(ppTimes, 90)),
            },
            'classification': {
                'min':  float(clsTimes.min()),
                'max':  float(clsTimes.max()),
                'mean': float(clsTimes.mean()),
                'std':  float(clsTimes.std()),
                'med':  float(np.median(clsTimes)),
                'p99':  float(np.percentile(clsTimes, 99)),
                'p90':  float(np.percentile(clsTimes, 90))
            },
            'combined': {
                'min':  float((ppTimes + clsTimes).min()),
                'max':  float((ppTimes + clsTimes).max()),
                'mean': float((ppTimes + clsTimes).mean()),
                'std':  float((ppTimes + clsTimes).std()),
                'med':  float(np.median(ppTimes + clsTimes)),
                'p99':  float(np.percentile(ppTimes + clsTimes, 99)),
                'p90':  float(np.percentile(ppTimes + clsTimes, 90)),
            }
        }
        dump(obj, out, indent=4)

    print('Finished writing report. End.')
    exit(0)


