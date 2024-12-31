const mqtt = require("mqtt");
const client = mqtt.connect("mqtt://mqtt.cheerlights.com");
const { DateTime } = require("luxon"); 

const express = require('express')
const app = express()
const port = process.env.PORT || 3000;
app.set('port',port);

const topic = client.subscribeAsync('color');

let color = "purple"
let messageArrivedAt = DateTime.utc();
//const colors = ["red","green","blue","purple","cyan","white", "magenta"]

client.on("message", (topic, message) => {
    color = message.toString()
    messageArrivedAt = DateTime.utc();
});

function getHexFromColor(color){
    let hexValue = ""
    switch (color) {
        case "red":
            hexValue = '#FF000';
            break;
        case "green":
            hexValue = '#008000';
            break;
        case "blue":
            hexValue = '#0000FF';
            break;
        case "cyan":
            hexValue = '#00FFFF';
            break;
        case "white":
            hexValue = '#FFFFFF';
            break;
        case "oldlace":
            hexValue = '#FDF5E6';
            break;
        case "purple":
            hexValue = '#800080';
            break;            
        case "magenta":
            hexValue = '#FF00FF';
            break;
        case "yellow":
            hexValue = '#FFFF00';
            break;
        case "orange":
            hexValue = '#FFA500';
            break;
        case "pink":
            hexValue = '#FFC0CB';
            break;                                            

    }
    return hexValue
}        


app.get('/', (req, res) => {

    //getRandomColor();
    res.status(200).send({'color' : color, 'hex': getHexFromColor(color), 'messageArrivedAt' : messageArrivedAt})
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})

function getRandomColor() {
    const probabilityOfChange = getRandomInt(1, 4);
    console.log("probabilityOfChange: " + probabilityOfChange);

    if (probabilityOfChange == 3) {

        const colorIndex = getRandomInt(0, 7);

        color = colors[colorIndex];
        messageArrivedAt = DateTime.utc();

        console.log("'new' color: " + color);
        console.log("'new' hex: " + getHexFromColor(color));
        console.log("messageArrivedAt: " + messageArrivedAt);

    }
}

function getRandomInt(min, max) {
  const minCeiled = Math.ceil(min);
  const maxFloored = Math.floor(max);
  return Math.floor(Math.random() * (maxFloored - minCeiled) + minCeiled); // The maximum is exclusive and the minimum is inclusive
}