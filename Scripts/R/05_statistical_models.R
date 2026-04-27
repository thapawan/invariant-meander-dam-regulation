#!/usr/bin/env Rscript
# Run Linear Mixed-Effects models and statistical tests
# Requires: lme4, lmerTest, performance, emmeans

library(lme4)
library(lmerTest)
library(performance)
library(emmeans)
library(dplyr)
library(tidyr)

prepare_model_data <- function() {
  # Load erodibility coefficients and covariates
  erodibility_data <- readRDS("output/phase_lag_erodibility_results.rds")
  covariates <- readRDS("data/processed/covariates_processed.rds")
  
  # Combine data from both rivers
  model_data <- bind_rows(
    erodibility_data$erodibility_coefficients$black_warrior %>%
      mutate(
        regulation_status = "regulated",
        river_id = "black_warrior"
      ),
    erodibility_data$erodibility_coefficients$cahaba %>%
      mutate(
        regulation_status = "unregulated", 
        river_id = "cahaba"
      )
  ) %>%
    # Join with covariates
    left_join(covariates$evi, by = "bend_id") %>%
    left_join(covariates$hydrology, by = c("river_id", "epoch")) %>%
    left_join(covariates$soils, by = "bend_id") %>%
    # Log-transform erodibility coefficient for normality
    mutate(
      log_erodibility = log(abs(erodibility_coefficient) + 0.001),
      regulation_status = factor(regulation_status, 
                                levels = c("unregulated", "regulated")),
      epoch = factor(epoch),
      bend_id = factor(bend_id)
    )
  
  return(model_data)
}

fit_linear_mixed_effects_model <- function(model_data) {
  # Full LME model specification from manuscript
  # log(E) ~ CV_Q + ΔEVI + Regulation + Clay + (ΔEVI * Regulation) + random effects
  
  lme_model <- lmer(
    log_erodibility ~ 
      flow_cv +                    # β1: Hydrologic forcing
      delta_evi +                  # β2: Vegetation change
      regulation_status +          # β3: Regulation status
      clay_content +               # β4: Geologic resistance
      delta_evi:regulation_status + # β5: Interaction term
      (1 | bend_id) +              # Random intercept for bend
      (1 | epoch),                 # Random intercept for temporal epoch
    data = model_data,
    REML = TRUE
  )
  
  return(lme_model)
}

validate_model_assumptions <- function(lme_model) {
  # Check model assumptions
  assumptions <- list()
  
  # Linearity and homoscedasticity
  assumptions$residual_plot <- plot(lme_model)
  
  # Normality of residuals
  assumptions$qq_plot <- qqnorm(resid(lme_model))
  
  # Check for multicollinearity
  assumptions$vif <- check_collinearity(lme_model)
  
  # Check random effects structure
  assumptions$random_effects <- ranef(lme_model)
  
  return(assumptions)
}

perform_hypothesis_tests <- function(model_data) {
  # Group comparisons for migration rates and erodibility
  
  # 1. Compare migration rates between rivers
  migration_test <- wilcox.test(
    median_migration_rate ~ regulation_status,
    data = model_data
  )
  
  # 2. Compare erodibility coefficients between rivers  
  erodibility_test <- wilcox.test(
    erodibility_coefficient ~ regulation_status,
    data = model_data
  )
  
  # 3. Flood-migration coupling test (Chi-squared)
  flood_data <- model_data %>%
    group_by(river_id, epoch) %>%
    summarize(
      high_migration = mean(median_migration_rate) > median(median_migration_rate),
      major_flood = any(flow_cv > quantile(flow_cv, 0.95))
    )
  
  flood_test <- chisq.test(
    table(flood_data$high_migration, flood_data$major_flood)
  )
  
  return(list(
    migration_comparison = migration_test,
    erodibility_comparison = erodibility_test,
    flood_coupling_test = flood_test
  ))
}

main <- function() {
  # Prepare analysis dataset
  model_data <- prepare_model_data()
  
  cat("Fitting Linear Mixed-Effects model...\n")
  
  # Fit the main LME model
  lme_model <- fit_linear_mixed_effects_model(model_data)
  
  # Model summary and coefficients
  model_summary <- summary(lme_model)
  coefficients <- coef(model_summary)
  
  # Extract key coefficients for interpretation
  key_results <- data.frame(
    predictor = rownames(coefficients),
    estimate = coefficients[, "Estimate"],
    std_error = coefficients[, "Std. Error"],
    p_value = coefficients[, "Pr(>|t|)"]
  )
  
  # Validate model assumptions
  model_validation <- validate_model_assumptions(lme_model)
  
  # Perform additional hypothesis tests
  hypothesis_tests <- perform_hypothesis_tests(model_data)
  
  # Calculate effect sizes for key predictors
  delta_evi_effect_regulated <- coefficients["delta_evi:regulation_statusregulated", "Estimate"]
  delta_evi_effect_unregulated <- coefficients["delta_evi", "Estimate"]
  
  # Compile all results
  results <- list(
    model_summary = model_summary,
    coefficients = key_results,
    model_validation = model_validation,
    hypothesis_tests = hypothesis_tests,
    effect_sizes = list(
      delta_evi_regulated = delta_evi_effect_regulated,
      delta_evi_unregulated = delta_evi_effect_unregulated,
      total_vegetation_effect = delta_evi_effect_regulated + delta_evi_effect_unregulated
    ),
    model_performance = r2(lme_model)
  )
  
  # Save complete results
  saveRDS(results, "output/statistical_analysis_results.rds")
  
  # Print key findings
  cat("\n=== KEY STATISTICAL RESULTS ===\n")
  cat("Vegetation effect (unregulated): β =", 
      round(delta_evi_effect_unregulated, 3), "\n")
  cat("Vegetation effect (regulated): β =", 
      round(delta_evi_effect_regulated, 3), "\n")
  cat("Migration rate comparison p-value:",
      round(hypothesis_tests$migration_comparison$p.value, 4), "\n")
  cat("Flood-migration coupling p-value:",
      round(hypothesis_tests$flood_coupling_test$p.value, 4), "\n")
  
  # Generate model diagnostic plots
  generate_model_diagnostics(lme_model, model_data)
}

if (sys.nframe() == 0) {
  main()
}
