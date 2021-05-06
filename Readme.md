# *tRackIT OS*: Experimental Evaluation Fragments
This repository contains the fragments of the experiments conducted for the research paper *tRackIT OS*: An open-source software for reliable VHF wildlife tracking. The data is analysed using Python3 and Jupyter, the respective notebooks, as well as the resulting figures are part of this repository.

## Experimentation Notebooks
- `processing_stages.ipynb` renders stages of data processing 
- `gps_tracks.ipynb` visualizes the experiement track
- `raw.ipynb` illustrates the analysis of the raw received signals
- `bearings.ipynb` aims to compare calculated and GPS-measured bearings
- `energy.ipynb` shows the energy usage comparison
- `time_drift.ipynb` shows the visualization of time drift observed in radio-tracking.eu's *paur*

## Repository Structure
The files in this repository are organized as follows:

```bash
├── fig
│   └── *.pdf                               # PDF renders of paper figures
├── rteu                                    # Experiment data of radio-tracking.eu's paur
│   ├── energy.csv                          # Energy measurements conducted in the lab
│   ├── gpstrack.csv                        # GPS track recorded during the experiment
│   ├── *_rteu_matched.csv                  # Matching of recorded signals and recorded GPS positions
│   ├── *_rteu_bearings.csv                 # Bearings calculated using matching of multiple antennas
│   ├── raw
│   │   └── *                               # Unprocessed signals
│   └── time_drift
│       └── time_drift_*.csv                # Examples of time drifts collected in field season 2020
├── tRackIT
│   ├── energy.csv
│   ├── gpstrack.csv
│   ├── *_tRackIT_matched.csv
│   ├── *_tRackIT_bearings.csv
│   └── raw
│       ├── *_2021-04-14T143517.csv         # Unprocessed signals
│       ├── *_2021-04-14T143517-matched.csv # On-device matched signals
│       └── *_2021-04-14T143517.ini         # Configuration pyradiotracking was started with
├── samples.pkl                             # One second of rtlsdr sampling data containing a signal @150.171 MHz, 40ms
├── stations.csv                            # List of stations used in experiments
└── *.ipynb                                 # Jupyter Notebooks used for Analysis
```

## Install dependencies

Depending on your system configuration, the required packages can be installed in various ways. The required python packages are: 
```
pandas
plotly
scipy
pytz
```