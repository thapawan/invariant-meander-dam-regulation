# Check distribution
hist(all_clay$claytotal_r, breaks = 20, 
     main = "Clay Content Distribution",
     xlab = "Clay (%)")

# Compare rivers
boxplot(claytotal_r ~ areasymbol, data = all_clay,
        main = "Clay Content by County",
        xlab = "County", ylab = "Clay (%)")
