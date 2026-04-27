# Query for specific Alabama counties
library(soilDB)

counties <- c("AL063", "AL065", "AL069", "AL073", "AL091", 
              "AL117", "AL119", "AL125")

clay_data <- list()

for (area in counties) {
  query <- paste0("
    SELECT areasymbol, mukey, compname, comppct_r,
           claytotal_r, hzdept_r
    FROM component
    JOIN mapunit ON component.mukey = mapunit.mukey
    JOIN legend ON mapunit.lkey = legend.lkey
    WHERE legend.areasymbol = '", area, "'
      AND hzdept_r = 0
      AND claytotal_r IS NOT NULL
  ")
  
  clay_data[[area]] <- SDA_query(query)
}

# Combine all results
all_clay <- do.call(rbind, clay_data)

# Calculate weighted average clay by soil component
summary_clay <- all_clay %>%
  group_by(areasymbol, compname) %>%
  summarise(
    clay_pct = weighted.mean(claytotal_r, comppct_r, na.rm = TRUE),
    .groups = 'drop'
  )

print(head(summary_clay))
