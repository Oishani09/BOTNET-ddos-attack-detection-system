const express = require('express');
const multer = require('multer');
const axios = require('axios');
const fs = require('fs');
const path = require('path');

const app = express();

// Set up multer for file uploads
const upload = multer({ dest: 'uploads/' });

// Route to handle file upload and forward it to the Flask server
app.post('/api/predict', upload.single('file'), async (req, res) => {
    if (!req.file) {
        return res.status(400).json({ error: 'No file uploaded' });
    }

    try {
        // Create a form-data payload for the Flask API
        const formData = new FormData();
        formData.append('file', fs.createReadStream(path.join(__dirname, req.file.path)), req.file.originalname);

        // Send the file to the Flask server
        const response = await axios.post('http://localhost:5000/api/predict', formData, {
            headers: {
                ...formData.getHeaders()
            }
        });

        // Clean up uploaded file
        fs.unlinkSync(req.file.path);

        // Send the prediction result back to the client
        res.json(response.data);
    } catch (error) {
        console.error('Error calling the Flask API:', error.message);
        res.status(500).json({ error: 'Error calling the Flask API' });
    }
});

// Start the Node.js server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Node server running on http://localhost:${PORT}`);
});
