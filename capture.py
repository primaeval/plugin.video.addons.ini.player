import re
import requests
from subprocess import call

f = open("index.html","w")
f.write('''<style>
    .img-wrap{
        width: 256; /*just here for the preview */
        height: 144;
        position: relative;
        float: left;
        margin: 10;        
    }
        .img-wrap img{
            max-width: 100%;
            z-index: 1
        }
        .img-wrap .caption{
            display: block;
            width: 256;
            position: absolute;
            bottom: 5px; /*if using padding in the caption, match here */
            left: 0;
            z-index: 2;
            margin: 0;
            padding: 5px 0;
            text-indent: 5px;
            color: #fff;
            font-weight: bold;
            background: rgba(0, 0, 0, 0.4);
        }
</style>''')

for s in ['','b']:
    for i in range(1,25):
        channelname = "sport_stream_%02d%s" % (i,s)
        caption = "Red Button %02d%s" % (i,s)
        print caption
        url = 'http://a.files.bbci.co.uk/media/live/manifesto/audio_video/%s/hls/uk/%s/%s/%s.m3u8' \
          % ('webcast', 'abr_hdtv', 'ak', channelname)
        r = requests.get(url)
        html = r.content
        for m in re.finditer(r'#EXT-X-STREAM-INF:PROGRAM-ID=(.+?),BANDWIDTH=(.+?),CODECS="(.*?)",RESOLUTION=(.+?)\s*(.+?.m3u8)',html):
            url = m.group(5)
            resolution = m.group(4)
            bitrate = m.group(2)
            print caption
            call(["ffmpeg", "-loglevel","quiet","-y", "-i", url, "-vframes", "1", "%s.png" % (channelname)])
            f.write('''<div class="img-wrap">
                        <img src="%s.png" alt= "">
                        <span class="caption">%s</span>
                        </div>
            ''' % (channelname,caption))
            break
f.close()
     