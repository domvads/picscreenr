# picscreenr

`picscreenr.py` is a small command line tool for storing image metadata
without using a database. Information is saved locally in a `metadata.json`
file and written into PNG image metadata using a `tEXt` chunk.

## Usage

Add metadata to an image:

```
python3 picscreenr.py add path/to/image.png --description "Description" --tags tag1 tag2
```

Read back stored metadata:

```
python3 picscreenr.py get path/to/image.png
```
