import React, { useState } from 'react';
import { Button, TextField, Box } from '@mui/material';
import { styled } from '@mui/material/styles';

// This is to style the input element
const Input = styled('input')({
    display: 'none',
});

function DatasetUpload({ onSuccess }) {
    const [file, setFile] = useState(null);
    const [filename, setFilename] = useState('');

    const handleFileChange = (event) => {
        setFile(event.target.files[0]);
        setFilename(event.target.files[0].name);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        if (!file) {
            alert('Please select a file to upload.');
            return;
        }

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                const data = await response.json();
                alert('File uploaded successfully');
                onSuccess(data.filename);
            } else {
                alert('File upload failed');
            }
        } catch (error) {
            console.error('Error during file upload:', error);
            alert('File upload failed');
        }
    };

    return (
        <Box sx={{ my: 2 }}>
            <form onSubmit={handleSubmit}>
                <label htmlFor="contained-button-file">
                    <Input
                        accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
                        id="contained-button-file"
                        multiple
                        type="file"
                        onChange={handleFileChange}
                    />
                    <Button variant="contained" component="span">
                        Choose file
                    </Button>
                    <TextField
                        sx={{ mx: 2 }}
                        disabled
                        label="File"
                        value={filename}
                        variant="outlined"
                    />
                    <Button variant="contained" color="primary" type="submit">
                        Upload Dataset
                    </Button>
                </label>
            </form>
        </Box>
    );
}

export default DatasetUpload;
