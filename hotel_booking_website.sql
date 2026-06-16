-- phpMyAdmin SQL Dump
-- version 2.11.6
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Oct 08, 2025 at 11:57 AM
-- Server version: 5.0.51
-- PHP Version: 5.2.6

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Database: `hotel_booking_website`
--

-- --------------------------------------------------------

--
-- Table structure for table `bookings`
--

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `room_id` int(11) NOT NULL,
  `check_in` date NOT NULL,
  `check_out` date NOT NULL,
  `adults` int(11) NOT NULL,
  `children` int(11) NOT NULL,
  `guests` int(11) NOT NULL,
  `payment_method` varchar(20) NOT NULL,
  `card_number` varchar(16) default NULL,
  `card_expiry` varchar(7) default NULL,
  `card_cvv` varchar(3) default NULL,
  `card_name` varchar(100) default NULL,
  `message` text,
  `status` varchar(20) default 'Pending',
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`),
  KEY `user_id` (`user_id`),
  KEY `room_id` (`room_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `bookings`

-- --------------------------------------------------------

--
-- Table structure for table `booking_meals`
--

CREATE TABLE `booking_meals` (
  `id` int(11) NOT NULL auto_increment,
  `booking_id` int(11) default NULL,
  `room_meal_id` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `booking_id` (`booking_id`),
  KEY `room_meal_id` (`room_meal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `booking_meals`
--


-- --------------------------------------------------------

--
-- Table structure for table `hotels`
--

CREATE TABLE `hotels` (
  `id` int(11) NOT NULL auto_increment,
  `hotel_name` varchar(255) NOT NULL,
  `location` varchar(255) NOT NULL,
  `contact` varchar(20) NOT NULL,
  `email` varchar(255) NOT NULL,
  `star` tinyint(4) NOT NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  `image_url` varchar(255) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `hotels`
--

-- --------------------------------------------------------

--
-- Table structure for table `rooms`
--

CREATE TABLE `rooms` (
  `id` int(11) NOT NULL auto_increment,
  `hotel_id` int(11) default NULL,
  `room_type` varchar(100) default NULL,
  `price` decimal(10,2) default NULL,
  `capacity` int(11) default NULL,
  `description` text,
  `amenities` text,
  `image` varchar(255) default NULL,
  `breakfast` varchar(500) default NULL,
  `lunch` varchar(500) default NULL,
  `dinner` varchar(500) default NULL,
  PRIMARY KEY  (`id`),
  KEY `hotel_id` (`hotel_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `rooms`
--

-- --------------------------------------------------------

--
-- Table structure for table `room_meals`
--

CREATE TABLE `room_meals` (
  `id` int(11) NOT NULL auto_increment,
  `room_id` int(11) NOT NULL,
  `meal_type` enum('breakfast','lunch','dinner') NOT NULL,
  `name` varchar(255) NOT NULL,
  `image_url` varchar(255) default NULL,
  PRIMARY KEY  (`id`),
  KEY `room_id` (`room_id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `room_meals`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  `age` int(11) default NULL,
  `contact` varchar(20) default NULL,
  `email` varchar(100) NOT NULL,
  `dob` date default NULL,
  `address` text,
  `gender` varchar(10) default NULL,
  `photo` varchar(255) default NULL,
  `password` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL default CURRENT_TIMESTAMP,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1 ;

--
-- Dumping data for table `users`
--

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`);

--
-- Constraints for table `booking_meals`
--
ALTER TABLE `booking_meals`
  ADD CONSTRAINT `booking_meals_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `booking_meals_ibfk_2` FOREIGN KEY (`room_meal_id`) REFERENCES `room_meals` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `rooms`
--
ALTER TABLE `rooms`
  ADD CONSTRAINT `rooms_ibfk_1` FOREIGN KEY (`hotel_id`) REFERENCES `hotels` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `room_meals`
--
ALTER TABLE `room_meals`
  ADD CONSTRAINT `room_meals_ibfk_1` FOREIGN KEY (`room_id`) REFERENCES `rooms` (`id`) ON DELETE CASCADE;
