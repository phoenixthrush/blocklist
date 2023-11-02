mkdir -p raw
mkdir -p output

rm -f raw/*.txt
rm -f output/*.txt

cd raw
count=0

while read -r url; do
  echo "Downloading: [$count] $url"
  filename="${count}.txt"
  curl -sSL "$url" >> "$filename".txt
  ((count++))
done < ../sources.txt

echo -e "\nProcessing files."
cp ../phoenixthrush.txt .
cat * > ../output/raw.txt

cd ../output
du -hs raw.txt

sort --parallel --ignore-leading-blanks --ignore-nonprinting --ignore-case raw.txt > sorted.txt
du -hs sorted.txt

uniq --ignore-case --unique sorted.txt unique.txt
du -hs unique.txt

cp unique.txt ..
