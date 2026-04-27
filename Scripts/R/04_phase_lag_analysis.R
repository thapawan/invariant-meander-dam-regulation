#!/usr/bin/env Rscript
# Determine optimal phase lag (Δs/W) for each river
# Requires: dplyr, purrr, ggplot2, lme4

library(dplyr)
library(purrr)
library(ggplot2)
library(lme4)

calculate_phase_lag_correlation <- function(migration_df, curvature_df, lag_distance, channel_width) {
  # Convert lag distance to normalized units (Δs/W)
  normalized_lag <- lag_distance / channel_width
  
  # Apply spatial lag to curvature
  curvature_lagged <- lag_curvature_spatially(curvature_df, lag_distance)
  
  # Merge migration and lagged curvature by bend ID and arc length
  merged_data <- migration_df %>%
    inner_join(curvature_lagged, by = c("bend_id", "arc_length_s"))
  
  # Calculate Spearman's rank correlation
  correlation_result <- cor.test(merged_data$migration_rate, 
                                merged_data$curvature_lagged,
                                method = "spearman")
  
  return(list(
    lag_distance = lag_distance,
    normalized_lag = normalized_lag,
    rho = correlation_result$estimate,
    p_value = correlation_result$p.value
  ))
}

find_optimal_phase_lag <- function(river_data, river_name) {
  # Candidate phase lags based on literature (in channel widths)
  candidate_lags_w <- c(1.5, 2.0, 2.5, 3.0)
  
  # Get channel width for normalization
  channel_width <- river_data$channel_width_median
  
  # Calculate correlations for each candidate lag
  lag_results <- map_df(candidate_lags_w, function(lag_w) {
    lag_distance_m <- lag_w * channel_width
    
    correlation_data <- calculate_phase_lag_correlation(
      river_data$migration_rates,
      river_data$curvature_profiles, 
      lag_distance_m,
      channel_width
    )
    
    return(data.frame(
      river = river_name,
      candidate_lag_w = lag_w,
      lag_distance_m = lag_distance_m,
      spearman_rho = correlation_data$rho,
      p_value = correlation_data$p_value
    ))
  })
  
  # Find optimal lag (maximum absolute correlation)
  optimal_lag <- lag_results %>%
    filter(spearman_rho == max(spearman_rho)) %>%
    slice(1)
  
  return(list(
    all_candidates = lag_results,
    optimal_lag = optimal_lag
  ))
}

calculate_erodibility_coefficient <- function(migration_data, curvature_data, optimal_lag_w) {
  # Calculate E = M / κ at optimal phase lag
  channel_width <- migration_data$channel_width_median
  optimal_lag_m <- optimal_lag_w * channel_width
  
  # Apply optimal lag to curvature
  curvature_lagged <- lag_curvature_spatially(curvature_data, optimal_lag_m)
  
  # Calculate erodibility coefficient for each bend
  erodibility_data <- migration_data$bend_migration %>%
    inner_join(curvature_lagged, by = "bend_id") %>%
    mutate(
      erodibility_coefficient = migration_rate_m_yr / curvature_lagged
    ) %>%
    filter(is.finite(erodibility_coefficient)) %>%
    filter(abs(erodibility_coefficient) < quantile(abs(erodibility_coefficient), 0.99, na.rm = TRUE))
  
  return(erodibility_data)
}

main <- function() {
  # Load planform metrics
  planform_metrics <- readRDS("data/processed/planform_metrics.rds")
  
  phase_lag_results <- list()
  erodibility_results <- list()
  
  # Analyze each river
  for(river_name in names(planform_metrics)) {
    cat("Analyzing phase lag for:", river_name, "\n")
    
    river_data <- planform_metrics[[river_name]]
    
    # Find optimal phase lag
    lag_analysis <- find_optimal_phase_lag(river_data, river_name)
    
    # Calculate erodibility coefficients using optimal lag
    optimal_lag_w <- lag_analysis$optimal_lag$candidate_lag_w
    erodibility_data <- calculate_erodibility_coefficient(
      river_data, river_data$curvature_profiles, optimal_lag_w
    )
    
    # Store results
    phase_lag_results[[river_name]] <- list(
      optimal_lag = lag_analysis$optimal_lag,
      all_candidates = lag_analysis$all_candidates,
      dimensionless_lag = optimal_lag_w
    )
    
    erodibility_results[[river_name]] <- erodibility_data
  }
  
  # Compare phase lags between rivers statistically
  regulated_lags <- phase_lag_results$black_warrior$all_candidates
  unregulated_lags <- phase_lag_results$cahaba$all_candidates
  
  # Mann-Whitney test for phase lag invariance
  phase_lag_test <- wilcox.test(
    regulated_lags$spearman_rho, 
    unregulated_lags$spearman_rho,
    alternative = "two.sided"
  )
  
  # Calculate Cliff's delta effect size
  cliff_delta <- orddom::dmes(regulated_lags$spearman_rho, 
                             unregulated_lags$spearman_rho)$dmes
  
  
  # Save results
  results <- list(
    phase_lag_analysis = phase_lag_results,
    erodibility_coefficients = erodibility_results,
    statistical_tests = list(
      mann_whitney_u = phase_lag_test$statistic,
      p_value = phase_lag_test$p.value,
      cliff_delta = cliff_delta
    )
  )
  
  saveRDS(results, "output/phase_lag_erodibility_results.rds")
  
  # Generate phase lag optimization plot (Figure 3b)
  generate_phase_lag_plot(phase_lag_results)
  
  cat("Phase lag analysis complete.\n")
  cat("Optimal phase lag - Black Warrior:", phase_lag_results$black_warrior$dimensionless_lag, "W\n")
  cat("Optimal phase lag - Cahaba:", phase_lag_results$cahaba$dimensionless_lag, "W\n")
  cat("Mann-Whitney U test p-value:", phase_lag_test$p.value, "\n")
}

if (sys.nframe() == 0) {
  main()
}
