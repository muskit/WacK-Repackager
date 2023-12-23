# Preparing files
This is a guide to populating the `data` folder, which will eventually contain all relevant data for repacking WACCA charts.

**This project will only repack audio on Reverse 3.07 properly.**

## Table of Contents
1. [Metadata](#metadata-datametadatajson)
2. [Charts](#charts-datamusicdata)
3. [Song Audio](#song-audio-datamer_bgm)
4. [Jackets](#jackets)

## Metadata (`data/metadata.json`)
1. Grab the latest [UAssetGUI](https://github.com/atenfyr/UAssetGUI).
2. Open `<WACCA>/app/WindowsNoEditor/Mercury/Content/Table/MusicParameterTable.uasset` with UAssetGUI.
3. In the toolbar, go to `File > Save As`.
4. Save it as a `UAssetAPI JSON` file in `data/metadata.json`.

We're done with UAssetGUI now. Feel free to close it.

## Charts (`data/MusicData`)
Simply copy the `<WACCA>/app/WindowsNoEditor/Mercury/Content/MusicData` folder into `data`.

## Song Audio (`data/MER_BGM`)
Due to the audio indexing data in this project only done for **Reverse 3.07**, these steps will only work for game files of that version.

You will need the latest version of [Audio Cue Editor (ACE)](https://github.com/LazyBone152/ACE).

For each of the files below located in `<WACCA>/app/WindowsNoEditor/Mercury/Content/Sound/Bgm`...

- MER_BGM.awb
- MER_BGM_V3_01.awb
- MER_BGM_V3_02.awb
- MER_BGM_V3_03.awb
- MER_BGM_V3_04.awb
- MER_BGM_V3_05.awb
- MER_BGM_V3_06.awb
- MER_BGM_V3_07.awb

...follow these directions on each file:

1. Create a folder in `data/MER_BGM` depending on the AWB file you're on:

| AWB File          | Folder in MER_BGM |
|-------------------|-------------------|
| MER_BGM.awb       | MER               |
| MER_BGM_V3_01.awb | 01                |
| MER_BGM_V3_02.awb | 02                |
| MER_BGM_V3_03.awb | 03                |
| MER_BGM_V3_04.awb | 04                |
| MER_BGM_V3_05.awb | 05                |
| MER_BGM_V3_06.awb | 06                |
| MER_BGM_V3_07.awb | 07                |

2. Load the file in ACE using `File > Load (AWB)`.
    - If asked to open the matching ACB, click "No."
3. Export all of the AWB's streams using `Tools > Extract All (wav)` into the folder you created earlier.

## Jackets
For the moment, this process pulls jackets available from WACCA's song listings website. This unfortunately means that some songs may not have a jacket.
