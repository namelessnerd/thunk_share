import React, { useState, useEffect } from 'react';
import {Box} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import UpdateIcon from '@mui/icons-material/Update';
import DeleteIcon from '@mui/icons-material/Delete';
import PublishIcon from '@mui/icons-material/Publish';
import UnpublishedIcon from '@mui/icons-material/Unpublished';
import TargetDemographics from './TargetDemographics';

import './creatives.css';

const CreativeItem = ({ id, targetDemo, headline, primaryText, description, callToAction }) => {
  // Randomly set published state
  const [isPublished, setIsPublished] = useState(false);

  useEffect(() => {
    setIsPublished(Math.random() < 0.5);
  }, []);

  const handlePublishToggle = () => {
    setIsPublished(!isPublished);
  };

  return (
    <Box sx={{ width: '50%', margin: '0 auto' }}>
        <div className="creative-item">
        <TargetDemographics targetDemo={targetDemo} />
        
        <div className="input-group">
            <div className="input-container">
            <label>Headline</label>
            <textarea className="text-box top-box" value={headline} readOnly rows="1" />
            </div>
            <div className="input-container">
            <label>Byline</label>
            <textarea className="text-box" value={description} readOnly rows="1"/>
            </div>
            <div className="input-container">
            <label>Creative Text</label>
            <textarea className="text-box" value={primaryText} readOnly rows="2" />
            </div>
        </div>
        <div className="actions">
            <label> Call to Action</label>
            <div className="cta-button">{callToAction}</div> {/* Changed from button to div */}
        </div>


        {/* Update, Delete, Publish/Unpublish buttons */}
        <div className="creative-actions">
        <button className="action-button" data-tooltip="Edit">
            <EditIcon sx={{ color: '#0D2ED3', marginRight: '5px' }} />
            </button>
            <button className="action-button" data-tooltip="Update">
            <UpdateIcon sx={{ color: '#0D2ED3', marginRight: '5px' }} />
            </button>
            <button className="action-button" data-tooltip="Delete">
            <DeleteIcon sx={{ color: 'red', marginRight: '5px' }} />
            </button>
            <button className="action-button" onClick={handlePublishToggle} data-tooltip={isPublished ? "Unpublish" : "Publish"}>
            {isPublished ? (
                <>
                <UnpublishedIcon sx={{ color: 'green', marginRight: '5px' }} />
                </>
            ) : (
                <>
                <PublishIcon sx={{ color: 'blue', marginRight: '5px' }} />
                </>
            )}
            </button>
        </div>
        </div>
    </Box>
  );
};

export default CreativeItem;

