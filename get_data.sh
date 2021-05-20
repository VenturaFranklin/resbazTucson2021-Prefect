cd data
if [ -x "$(command -v wget)" ]; then
  wget -c -i files.txt
  exit 1
else
  xargs -n 1 curl -O < files.txt
fi