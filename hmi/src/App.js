import React from 'react'
import {BrowserRouter as Router, Route, Routes} from "react-router-dom"
import Tags from './pages/Tags'
import Alarms from './pages/Alarms'
import Monitor from './pages/Monitor'
import Opcua from './pages/Opcua'
import Header from './components/Header'
import Aside from './components/Aside'
import Footer from './components/Footer'
import Configuration from './pages/Configuration'


export default function App() {
  return (
    <div className='wrapper'>
        <Header />
        
        <Router>
          <Aside />
            <Routes>
                <Route exact path='/' Component={Monitor}/>
                <Route exact path='/Tags' Component={Tags}/>
                <Route exact path='/Alarms' Component={Alarms}/>
                <Route exact path='/Opcua' Component={Opcua}/>
                <Route exact path='/Configuration' Component={Configuration}/>
            </Routes>
        </Router>
        <Footer />
    </div>
  )
}

