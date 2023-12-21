# Preparing files
I assume you have your desired game files ready. This guide is divided into the following prep sections:

1. [Metadata](###Metadata)
2. [Charts](###Charts)
3. [Song Audio](###Song%20Audio)
4. [Jackets](###Jackets)

Before beginning the process, I recommend creating a dedicated folder that will hold your prepared files. Throughout this guide, I will refer to this **working folder** as `repack`.

### Metadata (`repack/metadata.json`)
1. Grab the latest [UAssetGUI](https://github.com/atenfyr/UAssetGUI).
2. Open `<WACCA>/app/WindowsNoEditor/Mercury/Content/Table/MusicParameterTable.uasset` with UAssetGUI.
3. In the toolbar, go to `File > Save As`.
4. Save it as a `UAssetAPI JSON` file in `repack/metadata.json`.

We're done with UAssetGUI now. Feel free to close it.

### Charts (`repack/MusicData`)
Simply copy the `<WACCA>/app/WindowsNoEditor/Mercury/Content/MusicData` folder into `repack`.

### Song Audio (`repack/MER_BGM`)
This process is quite odd, and depending on the game files you have, you may end up with missing audio and/or mismatches. To minimize this, make sure you have the latest publicly available game files.

#### .awb Audio Stream Files
In `<WACCA>\app\WindowsNoEditor\Mercury\Content\Sound\Bgm`, copy `MER_BGM*.awb` into `repack/MER_BGM`. You will likely be copying the following files:
- MER_BGM.awb
- MER_BGM_V3_01.awb
- MER_BGM_V3_02.awb
- MER_BGM_V3_03.awb
- MER_BGM_V3_04.awb
- MER_BGM_V3_05.awb
- MER_BGM_V3_06.awb
- MER_BGM_V3_07.awb

#### .acb Files Creation
Have a binary-friendly editor ready. Notepad++ might work but could potentially mess things up due to encodings. I recommend using a hex editor like HxD instead.

1. Open `<WACCA>\app\WindowsNoEditor\Mercury\Content\Sound\Bgm\MER_BGM.uexp` in your binary editor of choice.
2. Delete any content leading up to the string `@UTF`. Most likely you will be deleting the first 0xDB bytes of the file. This edit should leave `@UTF` as the very first content of this file.
3. Save this edited file as `repack/MER_BGM/MER_BGM.acb`.
4. **For every .awb file in this working subfolder**, duplicate and rename your newly-created MER_BGM.acb after its file.
	- For example, if there exists `MER_BGM_V3_01.awb`, duplicate `MER_BGM.acb` as `MER_BGM_V3_01.acb`. And if there exists `MER_BGM_V3_02.awb`, duplicate `MER_BGM.acb` as `MER_BGM_V3_02.acb`, and so on...

#### Converting Audio
You will need the latest version of [Audio Cue Editor](https://github.com/LazyBone152/ACE) for this.

### Jackets
For the moment, this process pulls jackets available from WACCA's song listings website. This unfortunately means that some songs may not have a jacket.
