// import React, { useEffect, useState } from 'react';
// import axios from 'axios';

// function DisplayData() {
//   const [files, setFiles] = useState([]);
//   const [error, setError] = useState('');

//   useEffect(() => {
//     // Fetch the list of files from the backend
//     axios.get('http://www.neuroverse.co.in/files')
//       .then(response => {
//         setFiles(response.data);
//       })
//       .catch(error => {
//         setError('Error fetching files');
//       });
//   }, []);

  
//   const formatDate = (dateString) => {
//     const date = new Date(dateString);
//     return date.toISOString().split('T')[0];
//   };

//   return (
//     <div>
//       <h2>Uploaded Files</h2>
//       {error && <p style={{ color: 'red' }}>{error}</p>}
//       <table>
//         <thead>
//           <tr>
//             <th>Filename</th>
//             <th>Upload Date</th>
           
//           </tr>
//         </thead>
//         <tbody>
//           {files.map(file => (
//             <tr key={file.file_id}>
//               <td>{file.filename}</td>
//               <td>{formatDate(file.upload_date)}</td> 
              
//             </tr>
//           ))}
//         </tbody>
//       </table>
//     </div>
//   );
// }

// export default DisplayData;

import React, { useEffect, useState } from 'react';
import axios from 'axios';

function DisplayData() {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    // Fetch the list of files from the backend
    axios.get('http://www.neuroverse.co.in/files')
      .then(response => {
        setFiles(response.data);
      })
      .catch(error => {
        setError('Error fetching files');
      });
  }, []);

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toISOString().split('T')[0];
  };

  return (
    <div>
      <h2>Uploaded Files</h2>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      {files.length === 0 && !error && <p>No files found.</p>}
      {files.length > 0 && (
        <table>
          <thead>
            <tr>
              <th>Filename</th>
              <th>Upload Date</th>
              <th>File URL</th>
            </tr>
          </thead>
          <tbody>
            {files.map(file => (
              <tr key={file.file_id}>
                <td>{file.filename}</td>
                <td>{formatDate(file.upload_date)}</td>
                <td>
                  <a href={file.file_url} target="_blank" rel="noopener noreferrer">Download</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default DisplayData;

