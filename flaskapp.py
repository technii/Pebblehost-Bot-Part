from flask import Flask, request, jsonify, render_template, make_response, redirect
import random
from datetime import datetime, timezone
app = Flask(__name__)
images = ["https://cdn.discordapp.com/attachments/1265740184931143785/1510412056464195764/fatbilly.gif?ex=6a1cb858&is=6a1b66d8&hm=8dd4e3454ec84a77cc2e381e63a2d4f6c29e2cb34e2f4a260ae0f7d2e255f99f&","https://cdn.discordapp.com/attachments/755066782032724019/1509944722880204821/Holliday_Dave.png?ex=6a1c569b&is=6a1b051b&hm=75fc3e4b7ffbe554a86ed654fbb99f9543713ae730d93b14e051b044e6e607c2&","https://cdn.discordapp.com/attachments/1231286447131328544/1428093055713546401/viscous.gif?ex=6a1c834d&is=6a1b31cd&hm=6de58578bd86f49417f150b260eef2e0843fa5ad7c94aa03a8f740e5b74201ac&","https://cdn.discordapp.com/attachments/755066782032724019/1507070248182874243/image.png?ex=6a1c6d8b&is=6a1b1c0b&hm=70acabae4247b3ea74453c59928a06a8b37ad005a67a7fb2efa46e6bbd8f5e4b&","https://cdn.discordapp.com/attachments/755066782032724019/1505241591684530266/IMG_6383.jpg?ex=6a1c5df9&is=6a1b0c79&hm=6e99c6be366bde9260de83fa18c154bc70c7ccbc3c524ce716c9cda5d99e518b&","https://cdn.discordapp.com/attachments/755066782032724019/1422574535730921513/IMG_5691.jpg?ex=6a1c3647&is=6a1ae4c7&hm=debf88ad82f1a9069d03045a7e7c0dec2f73173f9aecd755206be5010589f0c8&"]

@app.route("/")
def home():
    image = images[random.randint(0,(len(images) - 1))]
    print(f"someone visited your site at {str.split(datetime.now(timezone.utc).astimezone().isoformat(),"T")}")
    return render_template("index.html", image = image)