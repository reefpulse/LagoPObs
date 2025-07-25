import sys
import os
import time
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showwarning, showerror, askyesno
from tkinter import filedialog
from tkinter import font
import numpy as np
import pandas as pd
from tools import utils, filtering, spectro, image_matching, pop_estimation

# Variables
# List of choices for overlap
overlap_list = [str(k) for k in range(5, 100, 5)]
# Default values for rock ptarmigan
default_lago_vars = [
    "Yes",
    "950",
    "2800",
    "281",
    "75",
    "706",
    "90",
    "53",
    "ORB custom",
    "Affinity Propagation",
    "Yes",
]
# Option for wavelet filtering
wlt_filt_list = ["Yes", "No"]
# Choice list for feature extraction algorithm
algo_features_list = ["SIFT", "ORB", "ORB custom", "AKAZE", "KAZE"]
# Choice list for clustering algorithm
algo_clustering_list = [
    "Affinity Propagation",
    "Agglomerative",
    "Bisecting K-Means",
    "Gaussian Mixture Model",
    "HDBSCAN",
    "K-Means",
    "Mean Shift",
]
# Choice for the estimation of population
estim_pop_list = ["Yes", "No"]


# Main window
class LagoPopObsUI(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        # Prepare the grid
        # Rows
        for i in range(21):
            self.grid_rowconfigure(i, weight=0)
        # Columns
        self.grid_columnconfigure(0, weight=1, uniform="same_group")
        self.grid_columnconfigure(1, weight=2, uniform="same_group")
        # Default configurations for each element of the grid
        default_grid = {"padx": 2, "pady": 2, "sticky": "nsew"}
        default_separator = {"padx": 10, "pady": 10, "sticky": "nsew"}
        # Window title
        self.title("lagoPObs")
        # Geometry of window
        self.geometry("1000x1000")
        self.resizable(True, False)
        # Variables of analysis
        self.dir_input = tk.StringVar(self, os.getcwd())
        self.dir_output = tk.StringVar(self, os.getcwd())
        self.wavelet_filt = tk.StringVar(self, default_lago_vars[0])
        self.fmin = tk.StringVar(self, default_lago_vars[1])
        self.fmax = tk.StringVar(self, default_lago_vars[2])
        self.win_fft = tk.StringVar(self, default_lago_vars[3])
        self.ovlp_fft = tk.StringVar(self, default_lago_vars[4])
        self.win_env = tk.StringVar(self, default_lago_vars[5])
        self.ovlp_env = tk.StringVar(self, default_lago_vars[6])
        self.n_matches = tk.StringVar(self, default_lago_vars[7])
        self.algo_features = tk.StringVar(self, default_lago_vars[8])
        self.algo_clustering = tk.StringVar(self, default_lago_vars[9])
        self.estim_pop = tk.StringVar(self, default_lago_vars[10])
        # Welcome text
        lab_welcome = ttk.Label(
            self,
            wraplength=1000,
            text="Welcome to the Lagopède Population Observator, in short LagoPObs, developped by Reef pulse SAS for the LPO AuRA (Ligue de Protection des Oiseaux Auvergne Rhône-Alpes). This software was designed initially to cluster rock ptarmigan males according to each type of their vocalisations, based on the differences of their spectrograms calculated with classical computer vision algorithms.\nPotentially, it could be used to separate other type of sounds by tinkering the analysis parameters but with no guarantee of results.\nThe software accepts sounds with different sampling frequencies and will resample each sound to the same sampling frequency, according to the highest frequency:\nsampling frequency = 2 x (highest frequency + 100)",
        )
        lab_welcome.grid(row=0, column=0, columnspan=2, **default_separator)
        # Separator
        ttk.Separator(self, orient="horizontal").grid(
            row=1, column=0, columnspan=2, sticky="ew"
        )
        lab_folders = ttk.Label(self, text="Folders")
        lab_folders.grid(row=2, column=0, columnspan=2, **default_separator)
        #  ttk.Separator(self, orient="horizontal").grid(row=1, column=1, columnspan=3, sticky='nse')
        # Input folder
        lab_dir_input = ttk.Label(text="Input folder containing wav files to analyze")
        lab_dir_input.grid(row=3, column=0, **default_grid, columnspan=2)
        button_dir_input = ttk.Button(
            self, text="Select input folder:", command=self.input_folder
        )
        button_dir_input.grid(row=4, column=0, **default_grid)
        self.text_dir_input = tk.Text(self, wrap="word", height=1)
        self.text_dir_input.insert("1.0", self.dir_input.get())
        self.text_dir_input.config(state="disabled")
        self.text_dir_input.grid(row=4, column=1, **default_grid)
        # Output folder
        lab_dir_output = ttk.Label(text="Output folder where the results will be saved")
        lab_dir_output.grid(row=5, column=0, columnspan=2, **default_grid)
        button_dir_output = ttk.Button(
            self, text="Select ouput folder:", command=self.output_folder
        )
        button_dir_output.grid(row=6, column=0, **default_grid)
        self.text_dir_output = tk.Text(self, wrap="word", height=1)
        self.text_dir_output.insert("1.0", self.dir_output.get())
        self.text_dir_output.config(state="disabled")
        self.text_dir_output.grid(row=6, column=1, **default_grid)
        # Separator
        ttk.Separator(self, orient="horizontal").grid(
            row=7, column=0, columnspan=2, sticky="ew", pady=20
        )
        lab_params = ttk.Label(text="Analysis parameters")
        lab_params.grid(row=8, column=0, columnspan=3, **default_separator)
        # Apply wavelet filtering or not?
        lab_wlt_filt = ttk.Label(text="Wavelet filtering:")
        lab_wlt_filt.grid(row=9, column=0, **default_grid)
        combo_wlt_filt = ttk.Combobox(self, textvariable=self.wavelet_filt)
        combo_wlt_filt["values"] = wlt_filt_list
        combo_wlt_filt["state"] = "readonly"
        combo_wlt_filt.grid(row=9, column=1, **default_grid)
        # Minimum frequency
        lab_fmin = ttk.Label(text="Lowest frequency:")
        lab_fmin.grid(row=10, column=0, **default_grid)
        entry_fmin = ttk.Entry(self, textvariable=self.fmin)
        entry_fmin.grid(row=10, column=1, **default_grid)
        # Maximum frequency
        lab_fmax = ttk.Label(text="Highest frequency:")
        lab_fmax.grid(row=11, column=0, **default_grid)
        entry_fmax = ttk.Entry(self, textvariable=self.fmax)
        entry_fmax.grid(row=11, column=1, **default_grid)
        # Window length for Short-Term Fourier Transform on sound
        lab_win_fft = ttk.Label(text="Window length for STFT of sound:")
        lab_win_fft.grid(row=12, column=0, **default_grid)
        entry_win_fft = ttk.Entry(self, textvariable=self.win_fft)
        entry_win_fft.grid(row=12, column=1, **default_grid)
        # Overlap in percent for Short-Term Fourier Transform on sound
        lab_ovlp_fft = ttk.Label(text="Overlap (in %) for STFT of sound:")
        lab_ovlp_fft.grid(row=13, column=0, **default_grid)
        combo_ovlp_fft = ttk.Combobox(self, textvariable=self.ovlp_fft)
        combo_ovlp_fft["values"] = overlap_list
        combo_ovlp_fft["state"] = "readonly"
        combo_ovlp_fft.grid(row=13, column=1, **default_grid)
        # Window length for Short-Term Fourier Transform on sound
        lab_win_env = ttk.Label(text="Window length for STFT of envelope:")
        lab_win_env.grid(row=14, column=0, **default_grid)
        entry_win_env = ttk.Entry(self, textvariable=self.win_env)
        entry_win_env.grid(row=14, column=1, **default_grid)
        # Overlap in percent for Short-Term Fourier Transform on envelope
        lab_ovlp_env = ttk.Label(text="Overlap (in %) for STFT of envelope:")
        lab_ovlp_env.grid(row=15, column=0, **default_grid)
        combo_ovlp_env = ttk.Combobox(self, textvariable=self.ovlp_env)
        combo_ovlp_env["values"] = overlap_list
        combo_ovlp_env["state"] = "readonly"
        combo_ovlp_env.grid(row=15, column=1, **default_grid)
        # Number of matches
        lab_n_matches = ttk.Label(text="Number of matches:")
        lab_n_matches.grid(row=16, column=0, **default_grid)
        entry_n_matches = ttk.Entry(self, textvariable=self.n_matches)
        entry_n_matches.grid(row=16, column=1, **default_grid)
        # Algorithm to extract features from images
        lab_algo_features = ttk.Label(text="Feature extraction algorithm:")
        lab_algo_features.grid(row=17, column=0, **default_grid)
        combo_algo_features = ttk.Combobox(self, textvariable=self.algo_features)
        combo_algo_features["values"] = algo_features_list
        combo_algo_features["state"] = "readonly"
        combo_algo_features.grid(row=17, column=1, **default_grid)
        # clustering algorithm
        lab_algo_clustering = ttk.Label(text="Clustering algorithm:")
        lab_algo_clustering.grid(row=18, column=0, **default_grid)
        combo_algo_clustering = ttk.Combobox(self, textvariable=self.algo_clustering)
        combo_algo_clustering["values"] = algo_clustering_list
        combo_algo_clustering["state"] = "readonly"
        combo_algo_clustering.grid(row=18, column=1, **default_grid)
        # Estimation of population?
        lab_pop_estim = ttk.Label(text="Population estimation:")
        lab_pop_estim.grid(row=19, column=0, **default_grid)
        combo_estim_pop = ttk.Combobox(self, textvariable=self.estim_pop)
        combo_estim_pop["values"] = estim_pop_list
        combo_estim_pop["state"] = "readonly"
        combo_estim_pop.grid(row=19, column=1, **default_grid)
        # Button to validate the parameters and proceed to analysis
        button_proceed = ttk.Button(
            self, text="Validate and proceed to analysis", command=self.validate_proceed
        )
        button_proceed.grid(row=20, column=0, columnspan=2, **default_separator)

    def input_folder(self):
        folder = filedialog.askdirectory(initialdir=self.dir_input.get())
        if folder != ():
            files = os.listdir(folder)
            wav_check = any([f.endswith(".wav") for f in files])
            if wav_check:
                self.text_dir_input.configure(state="normal")
                self.text_dir_input.delete("0.0", tk.END)
                self.text_dir_input.insert("1.0", folder)
                self.dir_input.set(folder)
                self.text_dir_output.configure(state="disabled")
            else:
                showwarning(
                    title="Wrong input folder!",
                    message="No WAV files in your input folder!",
                )

    def output_folder(self):
        folder = filedialog.askdirectory(initialdir=self.dir_output.get())
        if folder != ():
            self.text_dir_output.configure(state="normal")
            self.text_dir_output.delete("0.0", tk.END)
            self.text_dir_output.insert("1.0", folder)
            self.dir_output.set(folder)
            self.text_dir_input.configure(state="disabled")

    def update_progress(self, new_text="", add_value=20):
        value = self.progress_var.get()
        value += add_value
        if value > 100:
            value = 100
        self.progress_var.set(value)
        self.progress_bar["value"] = value
        text = self.text_pop.get()
        text += new_text
        self.text_pop.set(text)

    def validate_proceed(self):
        # Config font size
        font1 = font.Font(name="TkCaptionFont", exists=True)
        font1.config(size=11)
        # List with all problems
        list_problems = []
        # List with all warnings
        list_warnings = []
        # Check that input folder exists and contains WAV
        if os.path.isdir(self.dir_input.get()):
            files_input = os.listdir(self.dir_input.get())
            wav_check = any([f.endswith(".wav") for f in files_input])
            if not wav_check:
                list_problems.append("- Your input folder does not contain WAV files.")
        else:
            list_problems.append("- Your input folder does not exist.")
        # Check that output folder exists
        if not os.path.isdir(self.dir_output.get()):
            list_problems.append("- Your output folder does not exist.")
        # Check that the window length of both STFTs, minimum frequency, maximum frequency and number of matches are integers
        vars_value = [
            v.get()
            for v in [self.win_fft, self.win_env, self.fmin, self.fmax, self.n_matches]
        ]
        vars_name = [
            "window length",
            "envelope window length",
            "lowest frequency",
            "highest frequency",
            "number of matches",
        ]
        for v in zip(vars_value, vars_name):
            try:
                float_n = float(v[0])
            except ValueError:
                list_problems.append("- The %s is not a number." % (v[1]))
            else:
                if int(float_n) != float_n:
                    list_warnings.append(
                        "- The %s is a decimal, it will be rounded to the closest integer."
                        % (v[1])
                    )
        # Check that maximum frequency > minimum frequency
        if not any(["frequency" in p for p in list_problems]):
            if float(vars_value[2]) >= float(vars_value[3]):
                list_problems.append(
                    "- The lowest frequency is superior or equal to the highest frequency."
                )
        # Check that the number of matches to extract is not too high (>500)
        if not any(["matches" in p for p in list_problems]):
            if float(vars_value[-1]) > 500:
                list_problems.append(
                    "- The number of matches is too high (>500) compared to the number of extracted features."
                )
        # if there are any errors or warnings, display them
        if list_problems:
            list_problems += list_warnings
            list_problems = [
                "We cannot continue as several problems occured:"
            ] + list_problems
            showerror(title="Wrong inputs!", message="\n".join(list_problems))
        else:
            if list_warnings:
                list_warnings = [
                    "Several decimals were detected in the parameters:"
                ] + list_warnings
                showwarning(title="Floats in inputs!", message="\n".join(list_warnings))
            param_list = [
                "Input folder: ",
                "Output folder: ",
                "Apply wavelet filtering: ",
                "Lowest frequency: ",
                "Highest frequency: ",
                "Window length: ",
                "Overlap (%): ",
                "Envelope window length: ",
                "Envelope overlap (%): ",
                "Number of matches: ",
                "Feature extraction algorithm: ",
                "Clustering algorithm: ",
                "Estimation of population: ",
            ]
            param_values = [
                self.dir_input.get(),
                self.dir_output.get(),
                self.wavelet_filt.get(),
                str(round(float(self.fmin.get()))),
                str(round(float(self.fmax.get()))),
                str(int(float(self.win_fft.get()))),
                self.ovlp_fft.get(),
                str(int(float(self.win_env.get()))),
                self.ovlp_env.get(),
                str(int(float(self.n_matches.get()))),
                self.algo_features.get(),
                self.algo_clustering.get(),
                self.estim_pop.get(),
            ]
            param_valid = [p[0] + p[1] for p in zip(param_list, param_values)]
            param_valid = [
                "Do you wish to proceed with the following parameters?"
            ] + param_valid
            answer = askyesno(
                title="Validation of parameters", message="\n".join(param_valid)
            )
            if answer:
                # Display a secondary window
                self.popup = tk.Toplevel()
                self.popup.title("State")
                self.popup.grab_set()  # Main window is disabled
                # Text to display in popup
                self.text_pop = tk.StringVar(self, "Importing files...")
                lab_popup = ttk.Label(self.popup, textvariable=self.text_pop)
                lab_popup.grid(row=1, column=0, rowspan=11, columnspan=2)
                # Progress bar
                self.progress_var = tk.DoubleVar(self.popup, 0)
                self.progress_bar = ttk.Progressbar(
                    self.popup,
                    orient="horizontal",
                    mode="determinate",
                    variable=self.progress_var,
                    maximum=100,
                    length=350,
                )
                self.progress_bar.grid(row=0, column=0, columnspan=2, sticky="nsew")
                # Import list of WAVs
                list_wavs = utils.filter_wavs(param_values[0])
                list_arr, sf = utils.import_wavs(
                    list_wavs, param_values[0], int(param_values[4])
                )
                # Update window
                self.update_progress(new_text=" done!\nFiltering...")
                self.popup.update()
                # Filter with bandpass
                band_freq = [int(param_values[3]), int(param_values[4])]
                list_arr_filt = [
                    filtering.butterfilter(a, sf, band_freq) for a in list_arr
                ]
                # if wavelet filtering selected
                if param_values[2] == "Yes":
                    list_arr_filt = [filtering.wlt_denoise(a) for a in list_arr_filt]
                # Pad signals so that they have the same length
                arr_filt = utils.pad_signals(list_arr_filt)
                # Update window
                self.update_progress(new_text=" done!\nDrawing spectrograms...")
                self.popup.update()
                # Calculate spectrograms
                wlen = int(param_values[5])
                ovlp = int(param_values[6])
                wlen_env = int(param_values[7])
                ovlp_env = int(param_values[8])
                spectros = [
                    spectro.draw_specs(a, wlen, ovlp, wlen_env, ovlp_env, sf, band_freq)
                    for a in arr_filt
                ]
                # Update window
                self.update_progress(new_text=" done!\nClustering spectrograms...")
                self.popup.update()
                # Clustering spectrograms
                clusters, kp_desc = image_matching.cluster_spectro(
                    spectros, int(param_values[9]), param_values[10], param_values[11]
                )
                n_clust = len(np.unique(clusters))
                # Update window
                self.update_progress(
                    new_text=f" done, {n_clust} clusters found!\nSaving files..."
                )
                self.popup.update()
                # Save the clustering results
                # It is really important to create the DataFrame with a dict here
                # otherwise, you will create dobjects and it can impede the cluster order in the following result and thus impede the quality of the results.
                df_res = pd.DataFrame({"File": list_wavs, "Cluster": clusters})
                df_res.to_csv(param_values[1] + "/clustering_results.csv", index=False)
                # Save the spectrograms with the keypoints in it
                image_matching.save_spectros_keypoints(
                    spectros, kp_desc, list_wavs, param_values[1]
                )
                # Update window
                self.update_progress(new_text=" saved!\nAnalysis finished!")
                self.popup.update()
                # If population estimation is asked
                if param_values[12] == "Yes":
                    self.update_progress(new_text="\nPopulation estimation...")
                    self.popup.update()
                    try:
                        df_res_with_date = pop_estimation.add_date_to_df(df_res)
                    except ValueError:
                        showerror(
                            title="Wrong filename format!",
                            message="Population estimation not performed as the filenames format is wrong. Filenames must be split in different parts, separated by undescores, with the date in the second position and with the following format: yearmonthday. For example: 'xxxxx_20230619_xxxxxx.wav' means that the following file was recorded in June 13, 2023.",
                        )
                    else:
                        n_clusts_per_day = pop_estimation.daily_vocalize_clusters(
                            df_res_with_date
                        )
                        n_clusts_per_day.to_csv(
                            param_values[1] + "/number_of_clusters_per_day.csv",
                            index=False,
                        )
                        pres = pop_estimation.presence_clusters(df_res_with_date)
                        pres.to_csv(
                            param_values[1]
                            + "/number_of_sounds_per_cluster_per_date.csv"
                        )
                        pi_arr = pop_estimation.presence_index_arr(df_res_with_date)
                        pi_df = pd.DataFrame(
                            pi_arr,
                            columns=[
                                "Cluster",
                                "Days_of_presence",
                                "Number_of_sounds",
                                "Presence_index",
                            ],
                        )
                        sorted_pi_df = pi_df.sort_values(
                            by="Presence_index", ascending=False
                        )
                        sorted_pi_df.to_csv(
                            param_values[1] + "/presence_index.csv", index=False
                        )
                        # Estimation of resident individuals according to Presence Index
                        n_indiv_resident = np.count_nonzero(pi_arr[:, 3] >= 0.01)
                        # Estimation of the whole population using Population Information Criterion
                        pi_pop = pop_estimation.population_presence_index(pi_arr, pres)
                        n_indiv_tot, df_pic = (
                            pop_estimation.estimate_number_of_individuals(pi_pop)
                        )
                        df_pic.to_csv(param_values[1] + "/PPI_PIC.csv", index=False)
                        # Update window
                        self.update_progress(
                            new_text=f"done!\nEstimated number of individuals using PIC: {n_indiv_tot}\nEstimated number of resident individuals: {n_indiv_resident}"
                        )
                        self.popup.update()

                # Button to close the popup
                button_finish = ttk.Button(
                    self.popup,
                    text="Go back to main window",
                    command=self.popup.destroy,
                )
                button_finish.grid(row=12, column=0, columnspan=2)


if __name__ == "__main__":
    win = LagoPopObsUI()
    win.mainloop()
