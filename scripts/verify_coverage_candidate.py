"""Independent checks for the expanded candidate and actual Google subset fonts."""
from pathlib import Path
import sys,io,json,hashlib,itertools,unicodedata,zipfile
from fontTools.ttLib import TTFont
from fontTools import subset
from fontTools.pens.boundsPen import BoundsPen
import uharfbuzz as hb
import gfsubsets,gflanguages

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'build/coverage-verification'
OUT.mkdir(parents=True,exist_ok=True)
vf=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'candidates/1.314/SunnyMarker[opsz,slnt,wdth,wght].ttf'
if len(sys.argv)==1:
    snapshot=ROOT/'candidates/1.314'
    for line in (snapshot/'SHA256SUMS').read_text().splitlines():
        digest,name=line.split('  ',1)
        assert hashlib.sha256((snapshot/name).read_bytes()).hexdigest()==digest,name
# 1.314 is checked against the 1.313 release it extended, from the archived web package.
with zipfile.ZipFile(ROOT/'release/sunny-marker-web-1.313.zip') as archive:
    old=TTFont(io.BytesIO(archive.read('sunny-marker-web/webfonts/SunnyMarker-Variable-1.313.woff2')))
old.flavor=None;baseline=io.BytesIO();old.save(baseline);baseline=baseline.getvalue()
f=TTFont(vf);old=TTFont(io.BytesIO(baseline))
chars=set(f.getBestCmap());kept=set(old.getBestCmap())-{0x1ebc,0x1ebd}
assert kept<=chars
assert len(chars)==401 and len(f.getGlyphOrder())==416
assert set(range(0x10330,0x1034b))<=chars
assert {0x305,0x331}<=chars
assert not {0x1ebc,0x1ebd}&chars

def shape(font,order,text,loc):
    font.set_variations(loc)
    b=hb.Buffer();b.add_str(text);b.guess_segment_properties();hb.shape(font,b)
    return [(order[i.codepoint],p.x_advance,p.y_advance,p.x_offset,p.y_offset)
            for i,p in zip(b.glyph_infos,b.glyph_positions)]

a=hb.Font(hb.Face(baseline));b=hb.Font(hb.Face(vf.read_bytes()))
locations=list(itertools.product((300,400,550,700),(75,100,125),(10,23,36),(0,-4.5,-9)))
latin_checks=0;mark_checks=0
for values in locations:
    loc=dict(zip(('wght','wdth','opsz','slnt'),values))
    for cp in kept:
        assert shape(a,old.getGlyphOrder(),chr(cp),loc)==shape(b,f.getGlyphOrder(),chr(cp),loc),(cp,loc)
        latin_checks+=1
    for cp in list(range(0x10330,0x1034b))+list(map(ord,'AEIOUaeiou')):
        for mark in (0x304,0x305,0x331):
            result=shape(b,f.getGlyphOrder(),chr(cp)+chr(mark),loc)
            assert all(g[0]!='.notdef' for g in result),(cp,mark,loc)
            if cp>=0x10330:
                expected=shape(b,f.getGlyphOrder(),chr(cp),loc)
            else:
                # Soft-dot substitution uses the existing dotless-i metrics.
                # Compare with the released font's actual accent behavior.
                expected=shape(a,old.getGlyphOrder(),chr(cp)+chr(0x304 if mark==0x305 else mark),loc)
            assert sum(g[1] for g in result)==sum(g[1] for g in expected),(cp,mark,loc,result)
            mark_checks+=1
    gs=f.getGlyphSet(location=loc)
    for cp in range(0x10330,0x1034b):
        p=BoundsPen(gs);gs[f.getBestCmap()[cp]].draw(p)
        assert p.bounds and p.bounds[1]>=-340 and p.bounds[3]<=960,(cp,loc,p.bounds)

subdir=OUT/'subsets';subdir.mkdir(exist_ok=True)
union=set()
for name in ('gothic','latin','latin-ext'):
    selected=chars&set(gfsubsets.CodepointsInSubset(name,unique_glyphs=True))
    font=TTFont(vf)
    opts=subset.Options();opts.layout_features=['*'];opts.glyph_names=True
    opts.name_IDs=['*'];opts.name_languages=['*']
    ss=subset.Subsetter(options=opts);ss.populate(unicodes=selected);ss.subset(font)
    p=subdir/(name+'.ttf');font.save(p)
    font.flavor='woff2';font.save(subdir/(name+'.woff2'))
    union|=set(TTFont(p).getBestCmap())
langs=gflanguages.LoadLanguages()
sample_checks=0
for id in ('amr_Latn','ote_Latn','sey_Latn','got_Goth'):
    for field,txt in langs[id].sample_text.ListFields():
        if isinstance(txt,str):
            sample=unicodedata.normalize('NFC',txt).replace('\n','')
            assert set(map(ord,sample))<=union,(id,field.name,set(map(ord,sample))-union)
            result=shape(b,f.getGlyphOrder(),sample,dict(wght=400,wdth=100,opsz=14,slnt=0))
            assert all(g[0]!='.notdef' for g in result)
            sample_checks+=1
report={'glyphs':len(f.getGlyphOrder()),'codepoints':len(chars),
        'added_codepoints':[f'U+{c:04X}' for c in sorted(chars-set(old.getBestCmap()))],
        'removed_codepoints':['U+1EBC','U+1EBD'],'retained_latin_shaping_checks':latin_checks,
        'mark_checks':mark_checks,'axis_locations':len(locations),'routed_language_samples':sample_checks,
        'sha256':hashlib.sha256(vf.read_bytes()).hexdigest()}
(OUT/'verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
