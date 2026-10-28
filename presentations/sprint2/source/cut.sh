#!/bin/bash
# cut.sh in.mp4 out.mp4 "s1-e1 s2-e2 ..." : concatenate segments with 0.4 s fades
IN=$1; OUT=$2; SEGS=$3; i=0; F=""; L=""
for s in $SEGS; do a=${s%-*}; b=${s#*-}; d=$(python3 -c "print($b-$a)")
  F="$F[0:v]trim=$a:$b,setpts=PTS-STARTPTS,fade=t=in:st=0:d=0.3,fade=t=out:st=$(python3 -c "print($d-0.3)"):d=0.3[v$i];[0:a]atrim=$a:$b,asetpts=PTS-STARTPTS,afade=t=in:st=0:d=0.3,afade=t=out:st=$(python3 -c "print($d-0.3)"):d=0.3[a$i];"
  L="$L[v$i][a$i]"; i=$((i+1)); done
ffmpeg -y -loglevel error -i "$IN" -filter_complex "${F}${L}concat=n=$i:v=1:a=1[v][a]" -map "[v]" -map "[a]" -c:v libx264 -crf 21 -preset medium -pix_fmt yuv420p -c:a aac -b:a 160k -movflags +faststart "$OUT"
ffprobe -v error -show_entries format=duration -of csv=p=0 "$OUT"
