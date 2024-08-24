import React from 'react';
import PropTypes from 'prop-types';
import './RatingBar.css';

const RatingBar = ({ rating }) => {
  const getDescription = (rating) => {
    if (rating >= 10) return 'Perfect';
    if (rating >= 9) return 'Excellent';
    if (rating >= 8) return 'Very Good';
    if (rating >= 6) return 'Good';
    if (rating >= 5) return 'Fair';
    if (rating >= 4) return 'Needs Work';
    if (rating >= 2) return 'Poor';
    return 'Very Poor';
  };

  const getBarColor = (rating) => {
    if (rating >= 10) return '#7FFFFF'; // Blue
    if (rating >= 9) return '#7eff80'; // Green
    if (rating >= 8) return '#beff7f';  // Light Green
    if (rating >= 6) return '#feff7f';  // Yellow
    if (rating >= 5) return '#ffdf80';  // Orange
    if (rating >= 4) return '#ffbf7f';  // Deep Orange
    if (rating >= 2) return '##ff7f7e';  // Red
    return '#cfcfcf';  // Dark Red
  };

  const description = getDescription(rating);
  const barColor = getBarColor(rating);
  const barWidth = `${(rating / 10) * 100}%`;

  return (
    <div className="rating-bar">
      <div className="rating-bar-fill" style={{ width: barWidth, backgroundColor: barColor }}></div>
      <div className="rating-description">{description}</div>
    </div>
  );
};

RatingBar.propTypes = {
  rating: PropTypes.number.isRequired,
};

export default RatingBar;