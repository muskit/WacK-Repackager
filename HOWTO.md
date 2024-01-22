# Preparing files
This is a guide to populating the `data` working folder in this project's directory, which will eventually contain all relevant data for repacking WACCA charts. You may set up this folder elsewhere for storage space reasons; the app will let you choose a different working folder path. We will refer to this working folder as `data` throughout the guide.

Start with the `data` folder bundled with the app (or in the `dist` folder of this repo). Feel free to move it to another location as mentioned above.

**This project will only repack audio on Reverse 3.07 properly.**

## Table of Contents (sorted by descending time consumption)
1. [Videos](#videos-datamovies)
2. [Song Audio](#song-audio-datamer_bgm)
3. [Metadata](#metadata-datametadatajson)
4. [Jackets](#jackets)
5. [Charts](#charts-datamusicdata)

## Videos (`data/movies`)
*~4.1 GB*

If you want to export music videos, the process for doing so involves a **lot** of waiting. Therefore it is recommended to run this in the background while you do the other processes.

You will need [ffmpeg](https://www.ffmpeg.org/download.html) installed and on PATH.

1. Set the paths in `convert-videos.bat` as needed:
    - `video_path` to `<WACCA>/app/WindowsNoEditor/Mercury/Content/Movie`
    - `export_path` to `data/movies`
2. Run `convert-videos.bat` to convert all .usm videos to .mp4 in your working folder.
    - This script will take a **very** long time to finish. As mentioned earlier, I recommend running this in the background while you proceed to the next sections.

## Song Audio (`data/MER_BGM`)
*~18.8 GB for WAVs*

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

...follow these steps on each file:

1. Load the file in ACE using `File > Load (AWB)`.
    - If asked to open the matching ACB, click "No."
2. Export all of the AWB's streams using `Tools > Extract All (wav)` into a folder in `data/MER_BGM` depending on the current AWB file according to the table:

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

## Metadata (`data/metadata.json`)
*~5.6 MB*

You will need the latest [UAssetGUI](https://github.com/atenfyr/UAssetGUI).

1. Open `<WACCA>/app/WindowsNoEditor/Mercury/Content/Table/MusicParameterTable.uasset` with UAssetGUI.
2. In the toolbar, go to `File > Save As`.
3. Save it as a `UAssetAPI JSON` file in `data/metadata.json`.

## Jackets
*~54.4 MB*

For this, you will need [Unreal Engine resource viewer](https://www.gildor.org/en/projects/umodel)

1. Run `umodel_64.exe` and configure its Startup Options.
    - Set "Path to game files" to `<WACCA>/app/WindowsNoEditor/Mercury/Content/UI/Textures/JACKET`.
    - Enable "Override game detection" and set it to "Unreal engine 4.19."
    - Click OK.
2. In the left panel, right click on "All packages," then click on "Export folder content."
    - Under "Texture Export," set format to PNG, and the path to `data/jackets`.
    - Click OK to begin exporting jacket images.

## Charts (`data/MusicData`)
*~59.5 MB*
Simply copy the `<WACCA>/app/WindowsNoEditor/Mercury/Content/MusicData` folder into `data`.