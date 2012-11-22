find -type f -name \*.preset -exec sed -i -r 's/AlphaMin/rangeMin/g' {} \;
find -type f -name \*.preset -exec sed -i -r 's/AlphaMax/rangeMax/g' {} \;
