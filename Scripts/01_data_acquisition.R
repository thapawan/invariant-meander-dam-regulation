#!/usr/bin/env Rscript
# Satellite imagery acquisition and water mask generation
# Requires: googleEarthEngine, sf, raster packages

library(googleEarthEngine)
library(sf)
library(raster)

main <- function() {
  # Initialize GEE (requires prior authentication)
  ee_Initialize()
  
  # Study area boundaries
  black_warrior_bbox <- ee$Geometry$Rectangle(c(-87.8, 32.9, -87.2, 33.4))
  cahaba_bbox <- ee$Geometry$Rectangle(c(-87.1, 32.9, -86.8, 33.3))
  
  # Define analysis epochs
  epochs <- list(
    list(year = 2000, start_date = "2000-01-01", end_date = "2000-12-31"),
    list(year = 2018, start_date = "2018-01-01", end_date = "2018-12-31"), 
    list(year = 2024, start_date = "2024-01-01", end_date = "2024-12-31")
  )
  
  # Collection parameters
  get_image_collection <- function(bbox, start_date, end_date, year) {
    if (year == 2000) {
      # Landsat 5/7 for 2000
      col <- ee$ImageCollection("LANDSAT/LT05/C02/T1_L2")$
        filterBounds(bbox)$
        filterDate(start_date, end_date)$
        filter(ee$Filter$lt("CLOUD_COVER", 10))
    } else {
      # Sentinel-2 for 2018/2024
      col <- ee$ImageCollection("COPERNICUS/S2_SR_HARMONIZED")$
        filterBounds(bbox)$
        filterDate(start_date, end_date)$
        filter(ee$Filter$lt("CLOUDY_PIXEL_PERCENTAGE", 20))
    }
    return(col)
  }
  
  # Water classification using pre-trained DeepLabV3 model
  classify_water <- function(image) {
    # Load pre-trained model (path to your exported model)
    model <- ee$Model$fromAsset('users/your_username/deeplabv3_water_model')
    
    # Preprocess image for model input
    processed_image <- preprocess_for_model(image)
    
    # Run inference
    classification <- processed_image$classify(model)
    
    # Extract water class (class 1)
    water_mask <- classification$eq(1)
    
    return(water_mask)
  }
  
  # Process each epoch and river
  for(epoch in epochs) {
    cat("Processing epoch:", epoch$year, "\n")
    
    for(river_name in c("black_warrior", "cahaba")) {
      bbox <- get(paste0(river_name, "_bbox"))
      
      # Get image collection
      col <- get_image_collection(bbox, epoch$start_date, epoch$end_date, epoch$year)
      
      # Create median composite
      composite <- col$median()
      
      # Generate water mask
      water_mask <- classify_water(composite)
      
      # Export results
      output_name <- paste0(river_name, "_water_mask_", epoch$year)
      
      task <- ee_image_to_drive(
        image = water_mask,
        description = output_name,
        folder = "river_water_masks",
        scale = 10,
        region = bbox
      )
      
      task$start()
      cat("Started export task for", output_name, "\n")
    }
  }
  
  # Monitor task completion (simplified)
  cat("All export tasks started. Monitor progress in GEE Task Manager.\n")
}

if (sys.nframe() == 0) {
  main()
}
