RUNTIME=python3.7

SELENIUM_VER=4.6.0
CHROME_BINARY_VER=v1.0.0-57 
CHROMEDRIVER_VER=86.0.4240.22      

OUT_DIR=/out/layers/python/lib/$RUNTIME/site-packages

echo 'Working dir' $OUT_DIR

echo 'Downloading Selenium...'

docker run -v $(pwd):/out -it lambci/lambda:build-$RUNTIME \
    pip3 install selenium==$SELENIUM_VER -t $OUT_DIR

echo 'Compressing...'

cd layers/

zip -r layer_selenium_python.zip python/
#cp chrome_headless.py build/chrome_headless/python/chrome_headless.py

# pushd build/chrome_headless



echo 'Downloading Chrome Drivers...'

DRIVER_URL=https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VER/chromedriver_linux64.zip
curl -SL $DRIVER_URL > chromedriver.zip
unzip chromedriver.zip
rm chromedriver.zip

CHROME_URL=https://github.com/adieuadieu/serverless-chrome/releases/download/$CHROME_BINARY_VER/stable-headless-chromium-amazonlinux-2.zip
curl -SL $CHROME_URL > headless-chromium.zip
unzip headless-chromium.zip
rm headless-chromium.zip

echo 'Compressing...'

zip -r layer_chrome_selenium.zip chromedriver headless-chromium

rm -R python/
rm chromedriver 
rm headless-chromium