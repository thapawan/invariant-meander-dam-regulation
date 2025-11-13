#!/usr/bin/env Rscript
# Process covariates: ΔEVI, hydrology, soils
# Requires: terra, sf, jsonlite, httr

library(terra)
library(sf)
library(jsonlite)
library(httr)

calculate_evi <- function(red_band, nir_band, blue_band) {
  # Enhanced Vegetation Index calculation
  # EVI = 2.5 * (NIR - Red) / (NIR + 6 * Red - 7.5 * Blue + 1)
  2.5 * (nir_band - red_band) / (nir_band + 6 * red_band - 7.5 * blue_band + 1)
}

process_hydrology <- function() {
  # USGS NWIS data retrieval for flow variability
  usgs_base_url <- "https://waterservices.usgs.gov/nwis/dv/"
  
  gauges <- list(
    black_warrior = "02466030",
    cahaba = "02425000"
  )
  
  flow_data <- list()
  
  for(river_name in names(gauges)) {
    gauge_id <- gauges[[river_name]]
    
    # Construct API request
    url <- paste0(usgs_base_url, 
                  "?format=json&sites=", gauge_id,
                  "&startDT=2000-01-01&endDT=2024-12-31",
                  "&parameterCd=00060&statCd=00003")
    
    # Fetch data
    response <- GET(url)
    data <- fromJSON(rawToChar(response$content))
    
    # Calculate Coefficient of Variation (CV) by epoch
    daily_flows <- process_usgs_json(data)
    
    cv_2000_2018 <- calculate_flow_cv(daily_flows, "2000-01-01", "2018-12-31")
    cv_2018_2024 <- calculate_flow_cv(daily_flows, "2018-01-01", "2024-12-31")
    
    flow_data[[river_name]] <- list(
      cv_2000_2018 = cv_2000_2018,
      cv_2018_2024 = cv_2018_2024
    )
  }
  
  return(flow_data)
}

extract_soil_clay <- function(study_areas) {
  # Extract soil clay content from SSURGO
  # This is a simplified version - actual implementation would use soilDB package
  clay_data <- list()
  
  for(river_name in names(study_areas)) {
    area <- study_areas[[river_name]]
    
    # Buffer around river centerline
    riparian_buffer <- st_buffer(area, 200)
    
    # Query SSURGO (pseudo-code - actual implementation varies)
    clay_content <- query_ssurgo_clay(riparian_buffer)
    
    clay_data[[river_name]] <- clay_content
  }
  
  return(clay_data)
}

main <- function() {
  # Load study areas
  study_areas <- list(
    black_warrior = st_read("data/spatial/black_warrior_reach.shp"),
    cahaba = st_read("data/spatial/cahaba_reach.shp")
  )
  
  # Process ΔEVI between epochs
  evi_metrics <- calculate_delta_evi(study_areas)
  
  # Process hydrology
  flow_metrics <- process_hydrology()
  
  # Extract soil data
  soil_metrics <- extract_soil_clay(study_areas)
  
  # Combine all covariates
  covariates <- list(
    evi = evi_metrics,
    hydrology = flow_metrics, 
    soils = soil_metrics
  )
  
  # Save for statistical analysis
  saveRDS(covariates, "data/processed/covariates_processed.rds")
}

if (sys.nframe() == 0) {
  main()
}
