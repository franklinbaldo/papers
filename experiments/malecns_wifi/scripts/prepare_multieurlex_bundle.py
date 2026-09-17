"""Extract and save the 1,000-chunk MultiEURLEX-21 features bundle."""
import io
import urllib.request
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq


class HttpSeekableFile(io.RawIOBase):
    def __init__(self, url, size):
        self.url = url
        self.size = size
        self.pos = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, offset, whence=io.SEEK_SET):
        if whence == io.SEEK_SET:
            self.pos = offset
        elif whence == io.SEEK_CUR:
            self.pos += offset
        elif whence == io.SEEK_END:
            self.pos = self.size + offset
        return self.pos

    def readinto(self, b):
        l = len(b)
        if self.pos >= self.size or l == 0:
            return 0
        end = min(self.pos + l - 1, self.size - 1)
        req = urllib.request.Request(self.url, headers={'Range': f'bytes={self.pos}-{end}'})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
        b[:len(data)] = data
        self.pos += len(data)
        return len(data)


def main():
    out_path = Path("artifacts/runtime-v1/multieurlex-1000-features.npz")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    if out_path.exists():
        print(f"Target already exists at {out_path}")
        return

    print("Fetching labels from mteb test parquet...")
    url_mteb = 'https://huggingface.co/datasets/mteb/eurlex-multilingual/resolve/refs%2Fconvert%2Fparquet/pt/test/0000.parquet'
    f_mteb = io.BufferedReader(HttpSeekableFile(url_mteb, 26907289), buffer_size=1024 * 1024)
    pf_mteb = pq.ParquetFile(f_mteb)
    t_mteb = pf_mteb.read(columns=['id', 'label'])
    labels_by_id = {t_mteb['id'][i].as_py(): t_mteb['label'][i].as_py() for i in range(len(t_mteb))}

    print("Fetching cache parquet metadata...")
    url_cache = 'https://huggingface.co/datasets/franklinbaldo/multieurlex21-pt-semantic-cache/resolve/main/paraphrase-multilingual-minilm-l12-v2.parquet'
    f_cache = io.BufferedReader(HttpSeekableFile(url_cache, 174941125), buffer_size=4 * 1024 * 1024)
    pf = pq.ParquetFile(f_cache)
    table_meta = pf.read(columns=['id', 'split', 'split_index', 'chunk_index'])
    splits = table_meta['split'].to_pylist()
    ids = table_meta['id'].to_pylist()
    test_indices = [i for i, s in enumerate(splits) if s == 'test']
    first_1000 = test_indices[:1000]

    print("Extracting embeddings for first 1000 test chunks...")
    reader = pf.iter_batches(batch_size=10000, columns=['embedding'])
    count = 0
    embs = []
    for b in reader:
        prev = count
        count += len(b)
        if prev <= 110121 < count:
            start_in_b = 110121 - prev
            chunk_slice = b.slice(start_in_b, 1000)
            emb_list = chunk_slice['embedding'].to_pylist()
            embs = np.array(emb_list, dtype=np.float32)
            break

    doc_id_list = [ids[i] for i in first_1000]
    unique_docs = list(dict.fromkeys(doc_id_list))
    doc_to_group = {doc_id: idx for idx, doc_id in enumerate(unique_docs)}
    groups = np.array([doc_to_group[doc_id] for doc_id in doc_id_list], dtype=np.int64)

    tag_masks = np.zeros((1000, 21), dtype=np.float32)
    for i, doc_id in enumerate(doc_id_list):
        for lbl in labels_by_id.get(doc_id, []):
            tag_masks[i, lbl] = 1.0

    # Compute centroid tag embeddings from the positive test chunks
    centroids = np.zeros((21, 384), dtype=np.float32)
    for lbl in range(21):
        pos_mask = tag_masks[:, lbl] > 0
        if pos_mask.any():
            c = embs[pos_mask].mean(axis=0)
            centroids[lbl] = c / max(np.linalg.norm(c), 1e-12)
        else:
            centroids[lbl] = np.zeros(384, dtype=np.float32)

    print('Centroids shape:', centroids.shape)
    print('Centroid norms:', np.linalg.norm(centroids, axis=1))

    np.savez_compressed(
        out_path,
        absolute=embs,
        groups=groups,
        tag_masks=tag_masks,
        tag_embeddings=centroids,
        doc_ids=np.array(doc_id_list),
        unique_docs=np.array(unique_docs),
        chunk_indices=np.array([table_meta['chunk_index'][i].as_py() for i in first_1000]),
    )
    print('Saved input bundle to', out_path)


if __name__ == '__main__':
    main()
