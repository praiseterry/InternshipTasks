'use strict';

require('dotenv').config();
const express = require('express');
const bodyParser = require('body-parser');
const { encrypt, decrypt } = require('./crypto');

const app = express();
const PORT = process.env.PORT || 3000;

app.use(bodyParser.json());

app.post('/encrypt', (req, res) => {
    const { text } = req.body;
    if (!text) {
        return res.status(400).send('No text provided');
    }
    const encryptedText = encrypt(text);
    res.send({ encryptedText });
});

app.post('/decrypt', (req, res) => {
    const { encryptedText } = req.body;
    if (!encryptedText) {
        return res.status(400).send('No encrypted text provided');
    }
    const decryptedText = decrypt(encryptedText);
    res.send({ decryptedText });
});

app.listen(PORT, () => {
    console.log(`Server is running on port ${PORT}`);
});
