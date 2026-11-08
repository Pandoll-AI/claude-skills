#!/usr/bin/env python3
"""Data-driven Korean card-news renderer; Pillow + installed Korean fonts only."""
import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H, SCALE = 1122, 1402, 2
NAVY, BLUE, YELLOW = '#112747', '#2F70CD', '#FFC93B'
CREAM, WHITE, PALE = '#FCF9F3', '#FFFFFF', '#EAF1F9'
INK, MUTED, BORDER = '#152846', '#586D84', '#D7E2EF'
FONTS = [
    ('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc'),
    ('/System/Library/Fonts/AppleSDGothicNeo.ttc', '/System/Library/Fonts/AppleSDGothicNeo.ttc'),
    ('C:/Windows/Fonts/malgun.ttf', 'C:/Windows/Fonts/malgunbd.ttf'),
]


def find_fonts(user_regular=None, user_bold=None):
    if user_regular:
        reg = Path(user_regular)
        bold = Path(user_bold or user_regular)
        if not reg.is_file() or not bold.is_file():
            raise SystemExit('Requested font path does not exist.')
        return str(reg), str(bold)
    for a, b in FONTS:
        if Path(a).is_file() and Path(b).is_file():
            return a, b
    raise SystemExit('Install Noto Sans CJK, or pass --font and --font-bold. Fonts are not distributed.')


class Card:
    def __init__(self, index, total, date, fonts, dark=False):
        self.index, self.total, self.date, self.fonts, self.dark = index, total, date, fonts, dark
        self.im = Image.new('RGB', (W*SCALE, H*SCALE), NAVY if dark else CREAM)
        self.d = ImageDraw.Draw(self.im)
        self.bottom = 1250

    def xy(self, *p):
        return tuple(int(round(t*SCALE)) for t in p)

    def font(self, size, bold=False):
        return ImageFont.truetype(self.fonts[int(bool(bold))], int(size*SCALE))

    def measure(self, s, size, bold=False):
        bb = self.d.textbbox((0, 0), s, font=self.font(size, bold))
        return (bb[2]-bb[0])/SCALE

    def rect(self, x0, y0, x1, y1, fill, radius=18, outline=None):
        self.d.rounded_rectangle(self.xy(x0,y0,x1,y1), radius=int(radius*SCALE), fill=fill, outline=outline, width=2*SCALE)

    def text(self, x, y, s, size=34, colour=INK, bold=False):
        self.d.text(self.xy(x,y), str(s), fill=colour, font=self.font(size,bold), anchor='lt')

    def wrap(self, content, width, size, bold=False):
        lines=[]
        for paragraph in str(content).split('\n'):
            if not paragraph:
                lines.append(''); continue
            line=''
            for token in paragraph.split(' '):
                candidate=(line+' '+token).strip()
                if self.measure(candidate,size,bold)<=width:
                    line=candidate; continue
                if line:
                    lines.append(line); line=''
                if self.measure(token,size,bold)<=width:
                    line=token; continue
                # Character-level fallback for Korean and long unbroken words.
                for ch in token:
                    if self.measure(line+ch,size,bold)>width and line:
                        lines.append(line); line=''
                    line+=ch
            lines.append(line)
        return lines

    def paragraph(self, x,y,s,width,size=31,leading=1.45,colour=INK,bold=False,max_y=1260):
        for line in self.wrap(s,width,size,bold):
            if y + size*leading > max_y:
                raise ValueError(f'Card {self.index}: text exceeds available space near {line[:15]!r}')
            if line: self.text(x,y,line,size,colour,bold)
            y+=size*leading
        return y

    def chrome(self, section, title, source=''):
        fg=WHITE if self.dark else INK
        self.rect(76,70,360,125,YELLOW if self.dark else NAVY,28)
        self.text(96,82,section[:19],23,NAVY if self.dark else WHITE,True)
        self.rect(953,70,1046,119,WHITE if self.dark else NAVY,23)
        self.text(966,82,f'{self.index:02d}/{self.total:02d}',19,NAVY if self.dark else WHITE,True)
        self.paragraph(76,170,title,970,65,1.23,fg,True,max_y=480)
        self.d.line([self.xy(76,1321),self.xy(1046,1321)],fill='#657993' if self.dark else BORDER,width=2*SCALE)
        foot='#C3D4E9' if self.dark else MUTED
        if source: self.paragraph(76,1266,'출처: '+source[:125],965,19,1.25,foot,max_y=1318)
        self.text(76,1344,'CREATE CARDNEWS  ·  EVIDENCE FIRST',17,foot,True)
        self.text(947,1344,self.date,17,foot,True)

    def save(self, dest):
        self.im.resize((W,H),Image.Resampling.LANCZOS).save(dest,optimize=True)


def render(card, c):
    kind=card.get('type','bullets')
    c.chrome(card.get('label','핵심 요약'),card['title'],card.get('source',''))
    body_y=410
    if kind=='cover':
        subtitle=card.get('subtitle','')
        c.paragraph(82,720,subtitle,880,43,1.5,YELLOW,True,max_y=1110)
        c.rect(76,1155,1046,1230,'#27486C',26)
        c.text(111,1174,'언어별 성능  ·  실제 근거  ·  적용 가능성',31,WHITE,True)
    elif kind=='bullets':
        if card.get('intro'):
            body_y=c.paragraph(80,405,card['intro'],950,32,1.43,MUTED,max_y=700)+24
        items=card.get('items',[])
        if len(items)>5: raise ValueError('Max 5 items on a bullet card')
        each=min(178, int((1195-body_y)/max(len(items),1)))
        for i,item in enumerate(items):
            y=body_y+i*each
            c.rect(76,y,1046,y+each-13,WHITE,23,BORDER)
            c.rect(101,y+27,164,y+90,YELLOW,19)
            c.text(119,y+37,f'{i+1:02d}',25,NAVY,True)
            c.paragraph(195,y+18,item['head'],820,35,1.25,INK,True,max_y=y+83)
            if item.get('body'):
                c.paragraph(195,y+83,item['body'],808,27,1.38,MUTED,max_y=y+each-17)
    elif kind=='bars':
        metric=card.get('metric','')
        c.paragraph(82,391,metric,960,28,1.3,MUTED,max_y=460)
        bars=card.get('bars',[])
        if not 1<=len(bars)<=6: raise ValueError('Bar chart requires 1–6 rows')
        top=490; row_h=min(130,int(655/len(bars)))
        for i,bar in enumerate(bars):
            y=top+i*row_h
            label=bar['name']; value=float(bar['value']); full=float(card.get('max',100))
            if value<0 or value>full: raise ValueError('bar out of range')
            c.paragraph(82,y,label,940,30,1.2,INK,True,max_y=y+51)
            c.rect(82,y+51,920,y+91,PALE,20)
            if value>0: c.rect(82,y+51,82+838*value/full,y+91,YELLOW if i==0 else BLUE,20)
            c.text(935,y+53,f'{value:g}',31,INK,True)
        note_y=top+len(bars)*row_h+14
        if card.get('note'):
            c.rect(76,note_y,1046,1225,'#FFF1CD',22)
            c.paragraph(106,note_y+18,card['note'],908,27,1.38,INK,max_y=1216)
    elif kind=='table':
        headers=card.get('headers',[]); rows=card.get('rows',[])
        if not 2<=len(headers)<=3 or len(rows)>6: raise ValueError('2–3 columns and up to 6 rows required')
        widths=([400,570] if len(headers)==2 else [300,305,365])
        xstarts=[76];
        for w in widths[:-1]:xstarts.append(xstarts[-1]+w)
        top=429; head_h=85; row_h=min(131,int(665/max(len(rows),1)))
        c.rect(76,top,1046,top+head_h,NAVY,18)
        for j,h in enumerate(headers): c.paragraph(xstarts[j]+16,top+19,h,widths[j]-32,29,1.2,WHITE,True,max_y=top+head_h)
        for i,row in enumerate(rows):
            y=top+head_h+i*row_h
            c.rect(76,y,1046,y+row_h-3,WHITE if i%2==0 else PALE,8)
            for j,v in enumerate(row):
                c.paragraph(xstarts[j]+16,y+14,v,widths[j]-32,25,1.28,INK,bold=(j==0),max_y=y+row_h-10)
        if card.get('note'):
            c.paragraph(84,1160,card['note'],950,24,1.3,MUTED,max_y=1235)
    elif kind=='stats':
        stats=card.get('stats',[])
        if not 1<=len(stats)<=4: raise ValueError('Stats require 1–4 items')
        for i,v in enumerate(stats):
            col=i%2;row=i//2; x=76+col*492;y=425+row*365
            c.rect(x,y,x+475,y+345,WHITE,24,BORDER)
            c.paragraph(x+28,y+25,v['name'],420,29,1.24,INK,True,max_y=y+92)
            c.text(x+28,y+115,v['value'],74,BLUE,True)
            c.paragraph(x+28,y+235,v.get('detail',''),420,26,1.37,MUTED,max_y=y+338)
        if card.get('note'):
            c.rect(76,1190,1046,1250,'#FFF1CD',17)
            c.paragraph(91,1201,card['note'],940,23,1.25,INK,max_y=1248)
    elif kind=='conclusion':
        points=card.get('points',[])
        y=425
        for i,p in enumerate(points[:4]):
            c.rect(76,y,1046,y+153,WHITE,22,BORDER)
            c.rect(101,y+29,164,y+93,YELLOW,22)
            c.text(121,y+39,f'{i+1:02d}',27,NAVY,True)
            c.paragraph(190,y+31,p,810,31,1.38,INK,True,max_y=y+142)
            y+=174
        if card.get('note'):
            c.rect(76,1134,1046,1247,'#27486C',24)
            c.paragraph(104,1153,card['note'],910,27,1.28,WHITE,True,max_y=1239)
    else:
        raise ValueError(f'Unsupported type: {kind}')


def main():
    ap=argparse.ArgumentParser(description='Render Korean editorial card-news from a JSON deck')
    ap.add_argument('deck',type=Path)
    ap.add_argument('--output',type=Path,default=Path('cardnews-output'))
    ap.add_argument('--font')
    ap.add_argument('--font-bold')
    args=ap.parse_args()
    data=json.loads(args.deck.read_text(encoding='utf-8'))
    cards=data.get('cards',[])
    if not 1<=len(cards)<=20: raise SystemExit('Deck must contain 1–20 cards.')
    args.output.mkdir(parents=True,exist_ok=True)
    fonts=find_fonts(args.font,args.font_bold)
    thumbs=[]
    for idx,entry in enumerate(cards,1):
        c=Card(idx,len(cards),data.get('date',''),fonts,entry.get('type')=='cover')
        render(entry,c)
        name=f'{idx:02d}_{entry.get("type","card")}.png'
        c.save(args.output/name)
        thumbs.append(Image.open(args.output/name).convert('RGB'))
    tw=336; th=round(tw*H/W); columns=min(4,len(thumbs))
    rows=(len(thumbs)+columns-1)//columns
    sheet=Image.new('RGB',(columns*tw+(columns+1)*18,rows*th+(rows+1)*18),'#E7EAF0')
    for idx,im in enumerate(thumbs):
        x=18+(idx%columns)*(tw+18); y=18+(idx//columns)*(th+18)
        sheet.paste(im.resize((tw,th),Image.Resampling.LANCZOS),(x,y))
    sheet.save(args.output/'preview_contact_sheet.png')
    (args.output/'manifest.json').write_text(json.dumps({'size':[W,H],'count':len(cards),'source':data.get('source',''),'pages':[f'{i:02d}_{e.get("type","card")}.png' for i,e in enumerate(cards,1)]},ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'{len(cards)} cards written to {args.output}')


if __name__=='__main__':
    main()
