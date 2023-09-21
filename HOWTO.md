# Preparing files
I assume you have your desired game files ready. This guide is divided into the following prep sections:

1. [Metadata](###Metadata)
2. [Jackets](###Jackets)
3. [Song Audio](###Song%20Audio)

Before beginning the process, I recommend creating a dedicated folder that will hold your prepared files. As an example, I will refer to this theoretical **working folder** as `repack`.

### Metadata
1. Grab the latest [UAssetGUI](https://github.com/atenfyr/UAssetGUI).
2. Open `<WACCA>/app/WindowsNoEditor/Mercury/Content/Table/MusicParameterTable.uasset` with UAssetGUI.
3. In the toolbar, go to `File > Save As`.
4. Save it to your working folder as a `UAssetAPI JSON` file. I would save it to `repack/metadata.json`.

We're done with UAssetGUI now. Feel free to close it.

### Jackets
For the moment, this process pulls jackets available from WACCA's song listings website. This unfortunately means that some songs may not have a jacket.

### Song Audio
Make sure you have the latest publicly available game files. This process will likely not work with older files!