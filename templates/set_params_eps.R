#================================================#
# THIS FILE IS USED TO SET THE PARAMETERS 
# CONSIDERED BY THE VERIFICATION SCRIPTS AND THEIR
# ASSCOCIATED OPTIONS (E.G. SCALINGS, THRESHOLDS).
# 
# USE THE SAME FORMAT AS INDICATED BELOW IF
# ADDING ADDITIONAL PARAMETERS. REMEMBER TO 
# INCLUDE vc = "pressure" for UA PARAMETERS.
#
# INDICATIVE OBSMIN/MAX VALUES (OBS OUTSIDE OF 
# THIS RANGE ARE EXCLUDED) AND MAX NUMBER OF
# STANDARD DEVIATIONS (FOR check_obs_against_fcst)
# ARE INCLUDED
#
# models_to_scale CAN BE MISSING, NULL, OR
# TAKE THE FORM c("Model_A","Model_B",etc.)
#
#================================================#

params <- list(
    # Surface parameters
    T2m = list(
      thresholds = c(-20, -10, seq(-5, 25, 5)),
      scale_fcst = list(scaling = -273.15, new_units = "degC"),
      scale_obs  = list(scaling = -273.15, new_units = "degC"),
      obsmin_val = 273.15 - 30,
      obsmax_val = 273.15 + 50,
      error_sd   = 6,
      models_to_scale = NULL
    ),
    Td2m = list(
      thresholds = c(-20, -10, seq(-5, 30, 5)),
      scale_fcst = list(scaling = -273.15, new_units = "degC"),
      scale_obs  = list(scaling = -273.15, new_units = "degC"),
      obsmin_val = 273.15 - 30,
      obsmax_val = 273.15 + 50,
      error_sd   = 6
    ),
    Tmin = list(
      thresholds = c(seq(-15, 25, 5)),
      scale_fcst = list(scaling = -273.15, new_units = "degC"),
      scale_obs  = list(scaling = -273.15, new_units = "degC"),
      obsmin_val = 273.15 - 30,
      obsmax_val = 273.15 + 50,
      error_sd   = 6
    ),
    Tmax = list(
      thresholds = c(seq(0, 40, 5)),
      scale_fcst = list(scaling = -273.15, new_units = "degC"),
      scale_obs  = list(scaling = -273.15, new_units = "degC"),
      obsmin_val = 273.15 - 30,
      obsmax_val = 273.15 + 50,
      error_sd   = 6
    ),
    RH2m = list(
      thresholds = c(30,50,65,75,85,95),
      obsmin_val = 12.5,
      obsmax_val = 100,
      error_sd   = 6
    ),
    # Q2m typically in kg/kg in vobs/vfld files
    Q2m = list(
      thresholds = c(1,2.5,5,7.5,10), # In g/Kg
      scale_fcst = list(scaling = 1000, new_units = "g/Kg", mult = TRUE),
      scale_obs  = list(scaling = 1000, new_units = "g/Kg", mult = TRUE),
      obsmin_val = 0,
      obsmax_val = 50/1000, # Need to divide by the scale factor as filtering is done before scaling
      error_sd   = 6
    ),
    Pmsl = list(
      thresholds = c(seq(920, 1040, 20)),
      scale_fcst = list(scaling =0.01, new_units = "hPa", mult= TRUE),
      obsmin_val = 90000/100,
      obsmax_val = 106000/100,
      error_sd   = 6,
      use_models_to_scale = FALSE
    ),
    S10m = list(
      thresholds = c(2.5,5,7.5,10,15,20,25,30),
      scale_fcst = list(scaling = 0.0, new_units = "m/s"),
      scale_obs  = list(scaling = 0.0, new_units = "m/s"),
      obsmin_val = 0,
      obsmax_val = 100,
      error_sd   = 6
    ),
    Smax = list(
      thresholds = c(2.5,5,7.5,10,15,20,25,30),
      obsmin_val = 0,
      obsmax_val = 100,
      error_sd   = 6
    ),
    D10m = list(
      scale_fcst = list(scaling = 0, new_units = "degrees"),		
      thresholds = NULL,
      obsmin_val = 0,
      obmax_val  = 360,
      error_sd   = 6
    ),
    G10m = list(
      thresholds = c(2.5,5,7.5,10,15,20,25,30,35,40),
      obsmin_val = 0,
      obsmax_val = 100,
      error_sd   = 6
    ),
    Gmax = list(
      thresholds = c(2.5,5,7.5,10,15,20,25,30,35,40),
      scale_fcst = list(scaling = 0.0, new_units = "m/s"),
      scale_obs  = list(scaling = 0.0, new_units = "m/s"),
      obsmin_val = 0,
      obsmax_val = 100,
      error_sd   = 6
    ),
    AccPcp1h = list(
      thresholds = c(1,2.5,5,7.5),
      scale_fcst = list(scaling = 0.0, new_units = "kg/m^2"),
      scale_obs  = list(scaling = 0.0, new_units = "kg/m^2"),
      obsmin_val = 0,
      obsmax_val = 1000,
      error_sd   = 8
    ),
    Pcp = list(
      thresholds = c(0.1,0.5,1,2.5,5,7.5,10,15,20),
      scale_fcst = list(scaling = 0.0, new_units = "kg/m^2"),
      scale_obs  = list(scaling = 0.0, new_units = "kg/m^2"),
      obsmin_val = 0,
      obsmax_val = 1000,
      error_sd   = 8
    ),
    AccPcp3h = list(
      thresholds = c(0.1,0.5,1,2.5,5,7.5,10,15,20,25,30,40),
      scale_fcst = list(scaling = 0.0, new_units = "kg/m^2"),
      scale_obs  = list(scaling = 0.0, new_units = "kg/m^2"),
      obsmin_val = 0,
      obsmax_val = 1000,
      error_sd   = 8
    ),
    AccPcp6h = list(
      thresholds = c(0.1,0.5,1,2.5,5,7.5,10,15,20,25,30,40,50,60),
      scale_fcst = list(scaling = 0.0, new_units = "kg/m^2"),
      scale_obs  = list(scaling = 0.0, new_units = "kg/m^2"),
      obsmin_val = 0,
      obsmax_val = 1000,
      error_sd   = 8
    ),
    AccPcp12h = list(
      thresholds = c(0.1,0.5,1,2.5,5,7.5,10,15,20,25,30,40,50,60,70,80),
      scale_fcst = list(scaling = 0.0, new_units = "kg/m^2"),
      scale_obs  = list(scaling = 0.0, new_units = "kg/m^2"),
      obsmin_val = 0,
      obsmax_val = 1000,
      error_sd   = 8
    ),
    AccPcp24h = list(
      thresholds = c(0.1,0.5,1,2.5,5,7.5,10,15,20,25,30,40,50,60,70,80,90,100),
      scale_fcst = list(scaling = 0.0, new_units = "kg/m^2"),
      scale_obs  = list(scaling = 0.0, new_units = "kg/m^2"),
      obsmin_val = 0,
      obsmax_val = 1000,
      error_sd   = 8
    ),
    CCtot = list(
      thresholds = seq(0, 100, 20),
      scale_obs = list(scaling = 12.5, new_units = "%", mult= TRUE),
      scale_fcst = list(scaling = 100.0, new_units = "%", mult= TRUE),
      #models_to_scale=c("GDT_iekm","IFS"),
      models_to_scale=c("IFSENS"),
      obsmin_val = 0,
      obsmax_val = 8,
      error_sd   = 6
    ),
    CClow = list(
      thresholds = seq(0, 100, 20),
      scale_obs = list(scaling = 12.5, new_units = "%", mult= TRUE),
      scale_fcst = list(scaling = 100, new_units = "%", mult= TRUE),
      obsmin_val = 0,
      obsmax_val = 8,
      error_sd   = 6
    ),
    CCmed = list(
      thresholds = seq(0, 100, 20),
      scale_obs = list(scaling = 12.5, new_units = "%", mult= TRUE),
      scale_fcst = list(scaling = 100, new_units = "%", mult= TRUE),
      obsmin_val = 0,
      obsmax_val = 8,
      error_sd   = 6
    ),
    CChigh = list(
      thresholds = seq(0, 100, 20),
      scale_obs = list(scaling = 12.5, new_units = "%", mult= TRUE),
      scale_fcst = list(scaling = 100, new_units = "%", mult= TRUE),
      obsmin_val = 0,
      obsmax_val = 8,
      error_sd   = 6
    ),
    N75 = list(
      thresholds = seq(0, 100, 20),
      scale_obs = list(scaling = 12.5, new_units = "%", mult= TRUE),
      obsmin_val = 0,
      obsmax_val = 8,
      error_sd   = 6
    ),
    Cbase = list(
      thresholds = c(100,300,1000,2000,3000,5000),
      scale_fcst = list(scaling = 3.281, new_units = "ft", mult = TRUE),
      scale_obs  = list(scaling = 3.281, new_units = "ft", mult = TRUE),
      error_sd   = 6,
      obsmin_val = 0,
      obsmax_val = 24000,
      fctmax_val = 24000
    ),
    vis = list(
      thresholds = c(200,500,1000,4000),
      error_sd   = 6
    ),
    # Upper-air parameters
    S = list(
      scale_fcst = list(scaling = 0.0, new_units = "m/s"),
      scale_obs  = list(scaling = 0.0, new_units = "m/s"),
      vc         = "pressure"
    ),
    D = list(
       scale_fcst = list(scaling = 0, new_units = "degrees"),
       vc         = "pressure"
    ),
    Td = list(
      scale_fcst = list(scaling = -273.15, new_units = "degC"),
      scale_obs  = list(scaling = -273.15, new_units = "degC"),
      vc         = "pressure"
    ),
    Q = list(
      scale_fcst = list(scaling = 1000, new_units = "g/Kg", mult = TRUE),
      scale_obs  = list(scaling = 1000, new_units = "g/Kg", mult = TRUE),
      vc         = "pressure"
    ),
    RH = list(
      scale_fcst = list(scaling = 1, new_units = "%", mult = TRUE),
      scale_obs  = list(scaling = 1, new_units = "%", mult = TRUE),
	      
      vc         = "pressure"
    ),
    Z = list(
      vc         = "pressure"
    ),
    T = list(
      scale_fcst = list(scaling = -273.15, new_units = "degC"),
      scale_obs  = list(scaling = -273.15, new_units = "degC"),
      vc         = "pressure"
    )
)
