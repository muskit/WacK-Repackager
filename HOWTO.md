# Preparing files
I assume you have your desired game files ready. This guide is divided into the following prep sections:

1. [Metadata](##Metadata)
2. [Charts](##Charts)
3. [Song Audio](##Song%20Audio)
4. [Jackets](##Jackets)

Before beginning the process, I recommend creating a dedicated folder that will hold your prepared files. Throughout this guide, I will refer to this **working folder** as `repack`.

## Metadata (`repack/metadata.json`)
1. Grab the latest [UAssetGUI](https://github.com/atenfyr/UAssetGUI).
2. Open `<WACCA>/app/WindowsNoEditor/Mercury/Content/Table/MusicParameterTable.uasset` with UAssetGUI.
3. In the toolbar, go to `File > Save As`.
4. Save it as a `UAssetAPI JSON` file in `repack/metadata.json`.

We're done with UAssetGUI now. Feel free to close it.

## Charts (`repack/MusicData`)
Simply copy the `<WACCA>/app/WindowsNoEditor/Mercury/Content/MusicData` folder into `repack`.

## Song Audio (`repack/MER_BGM`)
At the moment this process is quite convoluted, and depending on the game files you have, you may end up with missing audio and/or mismatches. To minimize this, make sure you have the latest version (Reverse 3.07).

### .awb Audio Stream Files
In `<WACCA>\app\WindowsNoEditor\Mercury\Content\Sound\Bgm`, copy `MER_BGM*.awb` into `repack/MER_BGM`. For Reverse 3.07, it is these files:
- MER_BGM.awb
- MER_BGM_V3_01.awb
- MER_BGM_V3_02.awb
- MER_BGM_V3_03.awb
- MER_BGM_V3_04.awb
- MER_BGM_V3_05.awb
- MER_BGM_V3_06.awb
- MER_BGM_V3_07.awb

### .acb Files Creation
Have a binary-friendly editor ready. Notepad++ might work but could potentially mess things up due to encodings. I recommend using a hex editor like HxD instead.

1. Open `<WACCA>\app\WindowsNoEditor\Mercury\Content\Sound\Bgm\MER_BGM.uexp` in your binary editor of choice.
2. Delete any content leading up to the string `@UTF`. Most likely you will be deleting the first 0xDB bytes of the file. This edit should leave `@UTF` as the very first content of this file.
3. Save this edited file as `repack/MER_BGM/MER_BGM.acb`.
4. **For every .awb file in this working subfolder**, duplicate and rename your newly-created MER_BGM.acb after its file.
	- For example, if there exists `MER_BGM_V3_01.awb`, duplicate `MER_BGM.acb` as `MER_BGM_V3_01.acb`. And if there exists `MER_BGM_V3_02.awb`, duplicate `MER_BGM.acb` as `MER_BGM_V3_02.acb`, and so on...

**If you're working with Reverse 3.07, you should have these files so far:**
```
repack/
└── MER_BGM/
    ├── MER_BGM.acb
    ├── MER_BGM.awb
    ├── MER_BGM_V3_01.acb
    ├── MER_BGM_V3_01.awb
    ├── MER_BGM_V3_02.acb
    ├── MER_BGM_V3_02.awb
    ├── MER_BGM_V3_03.acb
    ├── MER_BGM_V3_03.awb
    ├── MER_BGM_V3_04.acb
    ├── MER_BGM_V3_04.awb
    ├── MER_BGM_V3_05.acb
    ├── MER_BGM_V3_05.awb
    ├── MER_BGM_V3_06.acb
    ├── MER_BGM_V3_06.awb
    ├── MER_BGM_V3_07.acb
    └── MER_BGM_V3_07.awb
```

### Converting Audio
Notice that we're working with two file types in this folder:
- **.awb** - essentially a bundle of unnamed audio streams.
- **.acb** - indexes for its associated .awb file. holds named "cues," which points to streams in the associated .awb.

WACCA splits up the BGM audio streams into different .awb files. However, there is only one .acb index file, which we've duplicated to correspond to each .awb. Our job now is to pair each of the .awb streams to its corresponding index in the .acb, which identifies the stream to a certain song ID. This method will work for *most* of the song audio. However, some .awb audio streams won't correspond to the .acb indexes we've just set up. Alternative methods are being looked into to recover erroneous audio streams.

You will need the latest version of [Audio Cue Editor (ACE)](https://github.com/LazyBone152/ACE) for this.

You will also need a lot of patience, as due to the odd formatting of these audio files, **every audio stream is going to be hand-extracted one by one.**

For each .acb file (starting with MER_BGM.acb)...
1. Load it into ACE.
2. Use the following table to extract the cue IDs for the ACB you're viewing.

| ACB File          | Cue IDs               |
|-------------------|-----------------------|
| MER_BGM.acb       | 1-350, 352-365, 373   |
| MER_BGM_V3_01.acb | 366-368               |
| MER_BGM_V3_02.acb | 369-371               |
| MER_BGM_V3_03.acb | 372,374               |
| MER_BGM_V3_04.acb | 375-383               |
| MER_BGM_V3_05.acb | 384-387, 389-390, 351 |
| MER_BGM_V3_06.acb | 391-394               |
| MER_BGM_V3_07.acb | 396-*                 |

You can ignore cues whose name isn't named formatted as "MER_BGM_Snn_nnn" (unless you want some system sounds).

3. When you click on a cue ID, two audio tracks will pop up. **The first one is the one you should extract.** The second is EQ'd differently, presumably for the cabinet speakers.
4. For each cue ID according to the table above, extract that first track audio to `repack/MER_BGM`.

Here are the audio streams that I couldn't find while assembling the table above:
```
S01-005: にめんせい☆ウラオモテライフ! - 土間うまる(田中あいみ)
S01-049: EZ DO DANCE -K.O.P. REMIX- - 仁科カヅキ vs 大和アレクサンダー(増田俊樹・武内駿輔)
S03-025: ∞(2018Remake) - cosMo＠暴走P feat.初音ミク
S03-026: おねがいダーリン - OИE (song by ナナホシ管弦楽団)
S03-024: 怪盗Fの台本（シナリオ）〜消えたダイヤの謎〜 - ひとしずく×やま△
S03-042: NightTheater - わかどり
S03-039: 恋のMoonlight - REDALiCE feat. 犬山たまき
S03-038: Comet Coaster - DJ Noriken & aran
S03-037: XODUS - DJ Myosuke & Gram
S03-036: Lights of Muse - Ayatsugu_Otowa
S02-036: ARTEMiS - BlackY
```

**This section took me probably a week to work out. Hopefully this process will no longer be necessary, as that should be needed is a batch-extract of the AWBs and a community-organized lookup table to programically pair the audio properly.**

## Jackets
For the moment, this process pulls jackets available from WACCA's song listings website. This unfortunately means that some songs may not have a jacket.
