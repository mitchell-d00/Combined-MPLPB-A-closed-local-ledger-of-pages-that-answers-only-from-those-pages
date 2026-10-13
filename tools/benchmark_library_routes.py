"""Synthetic catalog-breadth benchmark, NOT a full-library accuracy benchmark."""
import json
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path
from mplpb_combined.ledger import write
from mplpb_answers.library import Library


def run():
    rows=[]
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)/'selected'
        write(root,doc_id='S-1',title='Kettle',scope='kettle color',body='The kettle color is blue.')
        for size in (10,100,1000,5000):
            roots={'book'+str(i):('Book '+str(i),root if i==0 else Path(tmp)/'unopened') for i in range(size)}
            opened=[]
            tracemalloc.start(); start=time.perf_counter()
            catalog=Library(roots,resolve=lambda c:(opened.append(c) or roots[c][1]))
            build_ms=(time.perf_counter()-start)*1000
            _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
            timings=[]
            for _ in range(5):
                start=time.perf_counter();result=catalog.answer('What is the kettle color?','shelf-book0')
                timings.append((time.perf_counter()-start)*1000)
                assert result['kind']=='return'
            assert set(opened)=={'book0'}
            rows.append({'shelves':size,'selected_book_pages':1,'catalog_build_ms':round(build_ms,3),
                'catalog_peak_bytes':peak,'median_answer_ms':round(statistics.median(timings),3),
                'distinct_books_opened':len(set(opened))})
    return {'benchmark':'synthetic catalog breadth; preselected shelf; one-page selected book',
        'limitations':['Does not measure large-book scans, factual accuracy or real-library routing coverage.',
                       'Catalog is in memory; construction and storage grow with shelf count.',
                       'Supported answering still scans the selected corpus; costs are not zero.'], 'results':rows}

if __name__=='__main__':print(json.dumps(run(),indent=2))
