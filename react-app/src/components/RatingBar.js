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
    if (rating >= 0) return 'Very Poor';
    return 'Null';
  };

  const getBarColor = (rating) => {
    if (rating >= 10) return '#7fffff'; // Blue
    if (rating >= 9) return '#00ff00'; // Green
    if (rating >= 8) return '#7eff80';  // Light Green
    if (rating >= 6) return '#beff7f';  // Yellow-Green
    if (rating >= 5) return '#feff7f';  // Yellow
    if (rating >= 4) return '#ffdf80';  // Orange
    if (rating >= 2) return '#ffbf7f';  // Deep Orange
    if (rating >= 0) return '#ff7f7e';  // Red
    return '#bbb';
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