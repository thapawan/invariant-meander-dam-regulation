#install.packages(c("soilDB", "sf", "dplyr", "ggplot2"))
library(soilDB)
library(sf)
library(dplyr)

# Define study area boundaries (approximate coordinates for your reaches)
# Black Warrior River reach (50 km downstream of Selden Dam)
# Approximate bounding box - replace with your actual reach polygon
black_warrior_bbox <- st_bbox(c(xmin = -87.8, xmax = -87.5, 
                                 ymin = 32.5, ymax = 33.0), 
                               crs = 4326)

# Cahaba River reach (50 km from Centreville downstream)
cahaba_bbox <- st_bbox(c(xmin = -87.1, xmax = -86.8, 
                          ymin = 32.8, ymax = 33.2), 
                        crs = 4326)

# Function to extract clay content for a given area
extract_clay_data <- function(bbox, area_name) {
  # Query SSURGO data for the bounding box
  # This returns map unit keys and component data
  query <- paste0(
    "SELECT mukey, compname, comppct_r, ",
    "claytotal_r, hzdept_r, hzdepb_r, ",
    "nationalmusym, muname ",
    "FROM component ",
    "JOIN mapunit ON component.mukey = mapunit.mukey ",
    "WHERE mukey IN (SELECT DISTINCT mukey FROM mapunit ",
    "WHERE mukey IN (SELECT mukey FROM ssurgo_geo ",
    "WHERE ST_Intersects(geom, ST_GeomFromText('POLYGON((",
    paste(paste(bbox[c(1,2)], bbox[c(3,4)], sep = " "), collapse = ","),
    "))', 4326))))"
  )
  
  # Execute query via SDA
  result <- tryCatch({
    soilDB::SDA_query(query)
  }, error = function(e) {
    message("Query failed: ", e$message)
    return(NULL)
  })
  
  if (!is.null(result) && nrow(result) > 0) {
    # Filter to major components and surface horizons
    result <- result %>%
      filter(comppct_r >= 15,  # Major components only
             hzdept_r == 0)     # Surface horizon only
    
    # Calculate area-weighted average clay content
    clay_summary <- result %>%
      group_by(mukey, compname) %>%
      summarise(
        clay_content = weighted.mean(claytotal_r, comppct_r, na.rm = TRUE),
        component_pct = first(comppct_r),
        .groups = 'drop'
      )
    
    return(list(
      area = area_name,
      data = clay_summary,
      mean_clay = mean(clay_summary$clay_content, na.rm = TRUE),
      sd_clay = sd(clay_summary$clay_content, na.rm = TRUE)
    ))
  }
  return(NULL)
}

# Extract for both study areas
bw_clay <- extract_clay_data(black_warrior_bbox, "Black Warrior River")
cahaba_clay <- extract_clay_data(cahaba_bbox, "Cahaba River")

# Print results
cat("\n=== Clay Content Summary ===\n")
cat(sprintf("Black Warrior River: mean = %.1f%%, sd = %.1f%%\n", 
            bw_clay$mean_clay, bw_clay$sd_clay))
cat(sprintf("Cahaba River: mean = %.1f%%, sd = %.1f%%\n", 
            cahaba_clay$mean_clay, cahaba_clay$sd_clay))
