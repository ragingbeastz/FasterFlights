const http = require('http');
const fs = require('fs');
const path = require('path');

// Define the port to listen on
const PORT = 3000;

// Create the HTTP server
http.createServer((req, res) => {
    // Define the file path to serve
    const filePath = path.join(__dirname, 'pythonWebsite.html');

    // Read the HTML file
    fs.readFile(filePath, (err, content) => {
        if (err) {
            // If the file is not found, send a 404 response
            res.writeHead(404, { 'Content-Type': 'text/plain' });
            res.write('404 Not Found');
            res.end();
        } else {
            // If the file is found, serve it with a 200 response
            res.writeHead(200, { 'Content-Type': 'text/html' });
            res.write(content);
            res.end();
        }
    });
}).listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
});
