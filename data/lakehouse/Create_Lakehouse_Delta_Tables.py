# Databricks notebook source
# MAGIC %md
# MAGIC # Create Delta Tables for Retail Lakehouse
# MAGIC 
# MAGIC This notebook creates Delta Tables from the uploaded CSV/JSON files in the RetailLakehouse.
# MAGIC 
# MAGIC **Prerequisites:**
# MAGIC 1. Upload all files to the Lakehouse Files section
# MAGIC 2. Run this notebook in the context of your RetailLakehouse
# MAGIC 
# MAGIC **Tables to be created:**
# MAGIC - customer_service_interactions
# MAGIC - customer_feedback_comments
# MAGIC - customer_churn_analysis
# MAGIC - social_media_sentiment_analysis
# MAGIC - website_activity_log
# MAGIC - store_visit_history
# MAGIC - subscription_benefits_utilization

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Import Libraries

# COMMAND ----------

from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Define File Paths
# MAGIC 
# MAGIC Update these paths if your files are in a different location

# COMMAND ----------

# Base path for Lakehouse files
base_path = "Files/"

files = {
    "customer_service_interactions": f"{base_path}customer_service_interactions.json",
    "customer_feedback_comments": f"{base_path}customer_feedback_comments.csv",
    "customer_churn_analysis": f"{base_path}customer_churn_analysis.csv",
    "social_media_sentiment_analysis": f"{base_path}social_media_sentiment_analysis.csv",
    "website_activity_log": f"{base_path}website_activity_log.csv",
    "store_visit_history": f"{base_path}store_visit_history.csv",
    "subscription_benefits_utilization": f"{base_path}subscription_benefits_utilization.csv"
}

print("✅ File paths configured")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create Delta Table: customer_service_interactions
# MAGIC 
# MAGIC JSON file with service interaction transcripts

# COMMAND ----------

# Read JSON file
df_service = spark.read.option("multiLine", "true").json(files["customer_service_interactions"])

# Display schema and sample data
print("Schema:")
df_service.printSchema()
print(f"\nTotal records: {df_service.count()}")
display(df_service.limit(5))

# Write as Delta Table
df_service.write.format("delta").mode("overwrite").saveAsTable("customer_service_interactions")

print("✅ Delta Table 'customer_service_interactions' created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Create Delta Table: customer_feedback_comments
# MAGIC 
# MAGIC Customer feedback surveys with detailed text comments

# COMMAND ----------

# Read CSV file
df_feedback = spark.read.option("header", "true").option("inferSchema", "true").csv(files["customer_feedback_comments"])

# Display schema and sample data
print("Schema:")
df_feedback.printSchema()
print(f"\nTotal records: {df_feedback.count()}")
display(df_feedback.limit(5))

# Write as Delta Table
df_feedback.write.format("delta").mode("overwrite").saveAsTable("customer_feedback_comments")

print("✅ Delta Table 'customer_feedback_comments' created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Create Delta Table: customer_churn_analysis
# MAGIC 
# MAGIC Churn data with detailed cancellation reasons

# COMMAND ----------

# Read CSV file
df_churn = spark.read.option("header", "true").option("inferSchema", "true").csv(files["customer_churn_analysis"])

# Display schema and sample data
print("Schema:")
df_churn.printSchema()
print(f"\nTotal records: {df_churn.count()}")
display(df_churn.limit(5))

# Write as Delta Table
df_churn.write.format("delta").mode("overwrite").saveAsTable("customer_churn_analysis")

print("✅ Delta Table 'customer_churn_analysis' created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Create Delta Table: social_media_sentiment_analysis
# MAGIC 
# MAGIC Social media posts with sentiment scores and engagement metrics

# COMMAND ----------

# Read CSV file
df_social = spark.read.option("header", "true").option("inferSchema", "true").csv(files["social_media_sentiment_analysis"])

# Display schema and sample data
print("Schema:")
df_social.printSchema()
print(f"\nTotal records: {df_social.count()}")
display(df_social.limit(5))

# Write as Delta Table
df_social.write.format("delta").mode("overwrite").saveAsTable("social_media_sentiment_analysis")

print("✅ Delta Table 'social_media_sentiment_analysis' created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Create Delta Table: website_activity_log
# MAGIC 
# MAGIC Website session data with semi-structured page visit information

# COMMAND ----------

# Read CSV file
df_web = spark.read.option("header", "true").option("inferSchema", "true").csv(files["website_activity_log"])

# Display schema and sample data
print("Schema:")
df_web.printSchema()
print(f"\nTotal records: {df_web.count()}")
display(df_web.limit(5))

# Write as Delta Table
df_web.write.format("delta").mode("overwrite").saveAsTable("website_activity_log")

print("✅ Delta Table 'website_activity_log' created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Create Delta Table: store_visit_history
# MAGIC 
# MAGIC Physical store visit records with detailed outcome descriptions

# COMMAND ----------

# Read CSV file
df_store = spark.read.option("header", "true").option("inferSchema", "true").csv(files["store_visit_history"])

# Display schema and sample data
print("Schema:")
df_store.printSchema()
print(f"\nTotal records: {df_store.count()}")
display(df_store.limit(5))

# Write as Delta Table
df_store.write.format("delta").mode("overwrite").saveAsTable("store_visit_history")

print("✅ Delta Table 'store_visit_history' created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Create Delta Table: subscription_benefits_utilization
# MAGIC 
# MAGIC Loyalty program benefit usage with detailed engagement notes

# COMMAND ----------

# Read CSV file
df_benefits = spark.read.option("header", "true").option("inferSchema", "true").csv(files["subscription_benefits_utilization"])

# Display schema and sample data
print("Schema:")
df_benefits.printSchema()
print(f"\nTotal records: {df_benefits.count()}")
display(df_benefits.limit(5))

# Write as Delta Table
df_benefits.write.format("delta").mode("overwrite").saveAsTable("subscription_benefits_utilization")

print("✅ Delta Table 'subscription_benefits_utilization' created successfully")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 10. Verify All Tables Created

# COMMAND ----------

# List all tables in the Lakehouse
tables = spark.sql("SHOW TABLES").filter(col("isTemporary") == False)
display(tables)

print("\n" + "="*60)
print("✅ ALL DELTA TABLES CREATED SUCCESSFULLY!")
print("="*60)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 11. Sample Queries to Test Delta Tables

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query 1: Customer Service Interactions for Emily Thompson

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     interaction_id,
# MAGIC     date,
# MAGIC     channel,
# MAGIC     issue_type,
# MAGIC     satisfaction_rating,
# MAGIC     LEFT(transcript, 200) as transcript_preview
# MAGIC FROM customer_service_interactions
# MAGIC WHERE customer_name = 'Emily Thompson'
# MAGIC ORDER BY date DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query 2: Top Churn Reasons

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     LEFT(ReasonForCancellation, 100) as churn_reason_preview,
# MAGIC     COUNT(*) as frequency,
# MAGIC     AVG(ChurnRiskScore) as avg_risk_score
# MAGIC FROM customer_churn_analysis
# MAGIC GROUP BY LEFT(ReasonForCancellation, 100)
# MAGIC ORDER BY frequency DESC
# MAGIC LIMIT 10

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query 3: Social Media Sentiment Distribution

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     Platform,
# MAGIC     SentimentLabel,
# MAGIC     COUNT(*) as post_count,
# MAGIC     AVG(SentimentScore) as avg_sentiment,
# MAGIC     SUM(Engagement) as total_engagement
# MAGIC FROM social_media_sentiment_analysis
# MAGIC GROUP BY Platform, SentimentLabel
# MAGIC ORDER BY Platform, SentimentLabel

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query 4: Website Conversion Funnel

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     ConversionFlag,
# MAGIC     CartAbandonment,
# MAGIC     COUNT(*) as session_count,
# MAGIC     AVG(TimeOnSite) as avg_time_on_site
# MAGIC FROM website_activity_log
# MAGIC GROUP BY ConversionFlag, CartAbandonment

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query 5: Customer Feedback Sentiment by Product Category

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     ProductCategory,
# MAGIC     AVG(Rating) as avg_rating,
# MAGIC     AVG(SentimentScore) as avg_sentiment,
# MAGIC     COUNT(*) as feedback_count
# MAGIC FROM customer_feedback_comments
# MAGIC GROUP BY ProductCategory
# MAGIC ORDER BY avg_rating DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query 6: Store Visit Satisfaction by Purpose

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     Purpose,
# MAGIC     AVG(SatisfactionRating) as avg_satisfaction,
# MAGIC     COUNT(*) as visit_count,
# MAGIC     SUM(CASE WHEN PurchaseInStore = 'Yes' THEN 1 ELSE 0 END) as in_store_purchases
# MAGIC FROM store_visit_history
# MAGIC GROUP BY Purpose
# MAGIC ORDER BY avg_satisfaction DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ### Query 7: Loyalty Benefit Engagement by Tier

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT 
# MAGIC     LoyaltyTier,
# MAGIC     EngagementScore,
# MAGIC     COUNT(*) as member_months,
# MAGIC     AVG(TotalBenefitValue) as avg_benefit_value,
# MAGIC     SUM(PointsExpired) as total_points_expired
# MAGIC FROM subscription_benefits_utilization
# MAGIC GROUP BY LoyaltyTier, EngagementScore
# MAGIC ORDER BY LoyaltyTier, EngagementScore DESC

# COMMAND ----------

# MAGIC %md
# MAGIC ## 12. Table Statistics Summary

# COMMAND ----------

# Create summary of all tables
table_names = [
    "customer_service_interactions",
    "customer_feedback_comments", 
    "customer_churn_analysis",
    "social_media_sentiment_analysis",
    "website_activity_log",
    "store_visit_history",
    "subscription_benefits_utilization"
]

print("="*80)
print("DELTA TABLES SUMMARY")
print("="*80)

for table_name in table_names:
    count = spark.table(table_name).count()
    print(f"✅ {table_name:<40} | Records: {count:>6}")

print("="*80)
print("🎉 All Delta Tables are ready for Fabric Data Agent!")
print("="*80)
