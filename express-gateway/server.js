const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = 3000;
const MICROSERVICE_URL = 'http://localhost:8000';

app.use(cors());
app.use(express.json());

const handleAxiosError = (error, res) => {
    if (error.response) {
        console.error('Microservice Error:', error.response.data);
        res.status(error.response.status).json(error.response.data);
    } else if (error.request) {
        console.error('Microservice No Response:', error.request);
        res.status(503).json({ error: 'Microservice unavailable' });
    } else {
        console.error('Gateway Error:', error.message);
        res.status(500).json({ error: 'Internal Gateway Error' });
    }
};

// Retrieve all tasks
app.get('/tasks', async (req, res) => {
    try {
        const response = await axios.get(`${MICROSERVICE_URL}/tasks`);
        res.json(response.data);
    } catch (error) {
        handleAxiosError(error, res);
    }
});

// Retrieve a single task by ID
app.get('/tasks/:id', async (req, res) => {
    const taskId = req.params.id;
    try {
        const response = await axios.get(`${MICROSERVICE_URL}/tasks/${taskId}`);
        res.json(response.data);
    } catch (error) {
        handleAxiosError(error, res);
    }
});

// Create a new task
app.post('/tasks', async (req, res) => {
    try {
        const response = await axios.post(`${MICROSERVICE_URL}/tasks`, req.body);
        res.status(201).json(response.data);
    } catch (error) {
        handleAxiosError(error, res);
    }
});

// Record a submission for a task
app.post('/tasks/:id/submit', async (req, res) => {
    const taskId = req.params.id;
    try {
        const response = await axios.post(`${MICROSERVICE_URL}/tasks/${taskId}/submit`, req.body);
        res.status(201).json(response.data);
    } catch (error) {
        handleAxiosError(error, res);
    }
});

app.listen(PORT, () => {
    console.log(`Express Gateway running on port ${PORT}`);
    console.log(`Proxying requests to ${MICROSERVICE_URL}`);
});
