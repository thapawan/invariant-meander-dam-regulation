#!/usr/bin/env Rscript
# Generate all manuscript figures
# Requires: ggplot2, patchwork, ggpubr, sf, viridis

library(ggplot2)
library(patchwork)
library(ggpubr)
library(sf)
library(viridis)
library(dplyr)

create_figure_1 <- function() {
  # Study area map (Figure 1a-d)
  
  # Load spatial data
  alabama_map <- st_read("data/spatial/alabama_boundary.shp")
  watersheds <- st_read("data/spatial/huc8_watersheds.shp")
  study_reaches <- st_read("data/spatial/study_reaches.shp")
  centerlines <- readRDS("data/processed/centerlines_multitemporal.rds")
  
  # Create base map
  base_map <- ggplot() +
    geom_sf(data = alabama_map, fill = "white", color = "gray50") +
    geom_sf(data = watersheds, aes(fill = river_system), alpha = 0.6) +
    scale_fill_manual(values = c("Black Warrior" = "#E69F00", "Cahaba" = "#56B4E9")) +
    theme_minimal() +
    labs(title = "a) Regional Context")
  
  # Create reach maps with multitemporal centerlines
  black_warrior_map <- create_reach_map(centerlines$black_warrior, "b) Regulated Black Warrior River")
  cahaba_map <- create_reach_map(centerlines$cahaba, "c) Unregulated Cahaba River")
  
  # Combine using patchwork
  figure_1 <- base_map + black_warrior_map + cahaba_map +
    plot_layout(ncol = 2, heights = c(1, 1))
  
  ggsave("figures/Figure1_study_area.tiff", figure_1, 
         width = 8, height = 6, dpi = 300, compression = "lzw")
  
  return(figure_1)
}

create_figure_3 <- function() {
  # Phase lag analysis figure (Figure 3a-d)
  
  phase_lag_results <- readRDS("output/phase_lag_erodibility_results.rds")
  model_data <- readRDS("output/statistical_analysis_results.rds")
  
  # 3a: Unlagged correlation
  p3a <- ggplot(model_data, aes(x = abs_curvature, y = migration_rate)) +
    geom_point(alpha = 0.3, size = 1) +
    geom_smooth(method = "lm", se = FALSE, color = "red") +
    labs(x = "|Curvature| (m⁻¹)", y = "Migration Rate (m/yr)",
         title = "a) Unlagged Correlation") +
    theme_classic()
  
  # 3b: Phase lag optimization
  lag_data <- bind_rows(
    phase_lag_results$phase_lag_analysis$black_warrior$all_candidates,
    phase_lag_results$phase_lag_analysis$cahaba$all_candidates
  )
  
  p3b <- ggplot(lag_data, aes(x = candidate_lag_w, y = spearman_rho, color = river)) +
    geom_point(size = 3) +
    geom_line() +
    geom_errorbar(aes(ymin = spearman_rho - 0.1, ymax = spearman_rho + 0.1), width = 0.1) +
    scale_color_manual(values = c("black_warrior" = "#E69F00", "cahaba" = "#56B4E9")) +
    labs(x = "Candidate Phase Lag (Δs/W)", y = "Spearman's ρ",
         title = "b) Optimal Phase Lag Determination") +
    theme_classic()
  
  # 3c: Phase lag distributions
  p3c <- ggplot(lag_data, aes(x = river, y = spearman_rho, fill = river)) +
    geom_violin(alpha = 0.7) +
    geom_boxplot(width = 0.2, alpha = 0.9) +
    scale_fill_manual(values = c("black_warrior" = "#E69F00", "cahaba" = "#56B4E9")) +
    labs(x = "River", y = "Dimensionless Phase Lag (Δs/W)",
         title = "c) Phase Lag Distributions") +
    theme_classic()
  
  # 3d: Spatial invariance
  distance_data <- readRDS("data/processed/distance_from_dam.rds")
  p3d <- ggplot(distance_data, aes(x = distance_km, y = phase_lag_w)) +
    geom_point(alpha = 0.6) +
    geom_smooth(method = "lm", se = TRUE, color = "red") +
    labs(x = "Distance from Dam (km)", y = "Phase Lag (Δs/W)",
         title = "d) Spatial Invariance of Phase Lag") +
    theme_classic()
  
  # Combine subplots
  figure_3 <- (p3a + p3b) / (p3c + p3d) +
    plot_annotation(tag_levels = 'a')
  
  ggsave("figures/Figure3_phase_lag.tiff", figure_3, 
         width = 10, height = 8, dpi = 300, compression = "lzw")
  
  return(figure_3)
}

create_figure_4 <- function() {
  # Migration magnitude suppression (Figure 4a-c)
  
  model_data <- readRDS("output/statistical_analysis_results.rds")
  
  # 4a: Migration rate distributions
  p4a <- ggplot(model_data, aes(x = regulation_status, y = median_migration_rate, 
                               fill = regulation_status)) +
    geom_boxplot(alpha = 0.8) +
    scale_fill_manual(values = c("regulated" = "#E69F00", "unregulated" = "#56B4E9")) +
    labs(x = "Regulation Status", y = "Median Migration Rate (m/yr)",
         title = "a) Migration Rate Distributions") +
    theme_classic()
  
  # 4b: Empirical CDF
  p4b <- ggplot(model_data, aes(x = median_migration_rate, color = regulation_status)) +
    stat_ecdf(geom = "step", size = 1) +
    scale_color_manual(values = c("regulated" = "#E69F00", "unregulated" = "#56B4E9")) +
    labs(x = "Migration Rate (m/yr)", y = "Empirical CDF",
         title = "b) Cumulative Distribution") +
    theme_classic()
  
  # 4c: Migration variability (MAD)
  variability_data <- model_data %>%
    group_by(regulation_status) %>%
    summarize(
      mad_migration = mad(median_migration_rate)
    )
  
  p4c <- ggplot(variability_data, aes(x = regulation_status, y = mad_migration, 
                                     fill = regulation_status)) +
    geom_col(alpha = 0.8) +
    scale_fill_manual(values = c("regulated" = "#E69F00", "unregulated" = "#56B4E9")) +
    labs(x = "Regulation Status", y = "MAD of Migration Rate",
         title = "c) Migration Rate Variability") +
    theme_classic()
  
  figure_4 <- p4a + p4b + p4c +
    plot_layout(ncol = 3) +
    plot_annotation(tag_levels = 'a')
  
  ggsave("figures/Figure4_migration_suppression.tiff", figure_4, 
         width = 12, height = 4, dpi = 300, compression = "lzw")
  
  return(figure_4)
}

create_figure_5 <- function() {
  # Mechanism of suppression (Figure 5a-d)
  
  model_results <- readRDS("output/statistical_analysis_results.rds")
  covariates <- readRDS("data/processed/covariates_processed.rds")
  
  # 5a: Erodibility coefficient comparison
  p5a <- ggplot(model_results$model_data, 
                aes(x = regulation_status, y = erodibility_coefficient,
                    fill = regulation_status)) +
    geom_boxplot(alpha = 0.8) +
    scale_fill_manual(values = c("regulated" = "#E69F00", "unregulated" = "#56B4E9")) +
    labs(x = "Regulation Status", y = "Erodibility Coefficient (m²/yr)",
         title = "a) Erodibility Coefficient") +
    theme_classic()
  
  # 5b: Vegetation-erodibility relationship by regulation status
  p5b <- ggplot(model_results$model_data, 
                aes(x = delta_evi, y = erodibility_coefficient, 
                    color = regulation_status)) +
    geom_point(alpha = 0.5) +
    geom_smooth(method = "lm", se = TRUE) +
    scale_color_manual(values = c("regulated" = "#E69F00", "unregulated" = "#56B4E9")) +
    labs(x = "ΔEVI", y = "Erodibility Coefficient (m²/yr)",
         title = "b) Vegetation-Erodibility Relationship") +
    theme_classic()
  
  # 5c: Vegetation-clay relationship
  p5c <- ggplot(covariates, aes(x = clay_content, y = delta_evi)) +
    geom_point(alpha = 0.6) +
    geom_smooth(method = "lm", se = TRUE, color = "red") +
    labs(x = "Clay Content (%)", y = "ΔEVI",
         title = "c) Vegetation vs. Geologic Control") +
    theme_classic()
  
  # 5d: Flood-migration coupling
  flood_data <- model_results$hypothesis_tests$flood_coupling_data
  p5d <- ggplot(flood_data, aes(x = major_flood, y = high_migration_proportion, 
                               fill = regulation_status)) +
    geom_col(position = "dodge", alpha = 0.8) +
    scale_fill_manual(values = c("regulated" = "#E69F00", "unregulated" = "#56B4E9")) +
    labs(x = "Major Flood Event", y = "Proportion High Migration",
         title = "d) Flood-Migration Coupling") +
    theme_classic()
  
  figure_5 <- (p5a + p5b) / (p5c + p5d) +
    plot_annotation(tag_levels = 'a')
  
  ggsave("figures/Figure5_mechanisms.tiff", figure_5, 
         width = 10, height = 8, dpi = 300, compression = "lzw")
  
  return(figure_5)
}

main <- function() {
  cat("Generating manuscript figures...\n")
  
  # Create all figures
  fig1 <- create_figure_1()
  fig3 <- create_figure_3() 
  fig4 <- create_figure_4()
  fig5 <- create_figure_5()
  
  # Create supplementary figures
  source("scripts/06a_supplementary_figures.R")
  
  cat("All figures generated and saved to /figures/\n")
  cat("- Figure 1: Study area map\n")
  cat("- Figure 3: Phase lag analysis\n") 
  cat("- Figure 4: Migration suppression\n")
  cat("- Figure 5: Mechanism analysis\n")
}

if (sys.nframe() == 0) {
  main()
}
