import Header from "./Header.jsx";
import NavComp from "./Navbar/NavComp.jsx";
import { LineGraph } from "./LineChart.jsx";
import { Link } from "react-router-dom";
import Button from "react-bootstrap/Button";
import Footer from "./Footer.jsx";
import React from "react";
import Tickers from "./Screener/Tickers.jsx"


export const Screener = () => {
  return (
    <div className="primary-frame">
      <div className="logo-container">
        <Header />
      </div>

      <NavComp />

      <div className="secondary-frame">
        <Tickers />
        {/*<div className="lineChartGraph"><LineGraph /></div>*/}
      </div>
      {/*<Link to="https://www.youtube.com/watch?v=-mJFZp84TIY&list=PLu0W_9lII9agx66oZnT6IyhcMIbUMNMdt"><Button*/}
      {/*  style={{ marginLeft: '10px' }}>harry</Button></Link>*/}
    </div>
  );
};