import React, { useState, useEffect } from 'react';
import './Recommendation.css';
import './fonts.css';
import shy1 from '../image/shy1.png';
import shy2 from '../image/shy2.png';
import shy3 from '../image/shy3.png';
import bn1 from '../image/bn1.png';
import bn2 from '../image/bn2.png';
import bn3 from '../image/bn3.png';
import shree1 from '../image/shree1.png';
import shree2 from '../image/shree2.png';
import shree3 from '../image/shree3.png';
import ahemd1 from '../image/ahmed1.png';
import ahemd2 from '../image/ahmed2.png';
import ahemd3 from '../image/ahmed3.png';
import recom from '../image/recom-nobg.png';
import downArrowImageUrl from '../image/downarraow.png';
import { useLocation } from 'react-router-dom';
import Navbar from './NavBar';
import Image from './Image';
import TitleBlock from './TitleBlock';

const Recommendation = () => {
  const location = useLocation();
  const details = Array.isArray(location.state?.recommendations)
    ? location.state.recommendations
    : []; // Ensure it's an array
  const count = location.state?.count || 0;

  const shuffleArray = (array) => {
    for (let i = array.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [array[i], array[j]] = [array[j], array[i]];
    }
    return array;
  };

  const limitedDetails = details.slice(0, count);

  const shuffledDetails = count === 3 ? shuffleArray(limitedDetails) : limitedDetails;

  const [modalIsOpen, setModalIsOpen] = useState(null);

  const openModal = (index) => {
    setModalIsOpen(index);
  };

  const closeModal = () => {
    setModalIsOpen(null);
  };

  return (
    <div>
      <Navbar />
      <div className="recommendation-container" style={{ backgroundColor: '#D9D9D9' }}>
        <TitleBlock title="Our Top Suggestions:" />
        <div className="restaurant-list">
          {shuffledDetails.length === 0 ? (
            <div className="no-restaurants">No similar restaurants found</div>
          ) : (
            shuffledDetails.map((restaurant, index) => (
              <div className="restaurant-item" key={index}>
                <div className="restaurant-image-wrapper">
                  <div className="restaurant-image">
                    <Image
                      place={restaurant.location}
                      filename={`${restaurant.img_name}.jpg`}
                    />
                  </div>
                </div>
                <div className="restaurant-details">
                  <h3 className="restaurant-name">
                    {index + 1}. {restaurant.restaurant_name}
                  </h3>
                  <p className="restaurant-dishes">Feature Opinions: {restaurant.feature_opinions}</p>
                </div>

                <div className="restaurant-cuisine-cost">
                  <p className="restaurant-cuisine">Similarity Rank: {index + 1}</p>
                  <p class="restaurant-location">Location: {restaurant.location}</p>
                  <p className="restaurant-rating">Rating: {restaurant.rating}</p>
                  <p className="restaurant-cuisine">Cuisine: {restaurant.type}</p>
                  <p className="restaurant-cost">Budget: {restaurant.budget}</p>
                </div>

                <button
                  className="transparent-button"
                  onClick={() => openModal(index)}
                >
                  <img
                    src={downArrowImageUrl}
                    alt="View Details"
                  />
                </button>

                {modalIsOpen === index && (
                  <div className="modal">
                    <div className="image-row">
                      <div className="image-container">
                        <h3>Rating Analysis</h3>
                        <Image
                          place={restaurant.location}
                          filename={`${restaurant.restaurant_name}_rating_graph.jpg`}
                        />
                      </div>
                      <div className="image-container">
                        <h3>Review Analysis</h3>
                        <Image
                          place={restaurant.location}
                          filename={`${restaurant.restaurant_name}_sentiment_graph.jpg`}
                        />
                      </div>
                      <span
                        className="close-btn"
                        onClick={closeModal}
                      >
                        &times;
                      </span>
                    </div>
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Recommendation;
