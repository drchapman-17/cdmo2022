import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


"""""""""""""""""""""""""""""""""""""""
SETTA QUESTI PARAMETRI COME PREFERISCI
"""""""""""""""""""""""""""""""""""""""

save_image=True
csv_no_rotation = 'report_SMT.csv'
csv_rotation = 'report_SMT_rotation.csv'
name_image = 'report_SMT.png'

df = pd.read_csv(csv_no_rotation, sep=';')
df_flip = pd.read_csv(csv_rotation, sep=';')

df.loc[df['Time'] > 300, 'Time']= 300
df_flip.loc[df_flip['Time'] > 300, 'Time']= 300

df['mode'] = 'No rotation'
df_flip['mode'] = 'Rotation'

df.loc[df['Time'] > 299, 'mode']= 'Timeout no rotation'
df_flip.loc[df_flip['Time'] > 299, 'mode']= 'Timeout rotation'

df = pd.concat([df, df_flip])

sns.set_palette(sns.color_palette("tab10"))
plt.figure(figsize = (15,10))
sns.barplot(data = df, x = 'Instance', y = 'Time', hue = 'mode', hue_order=['No rotation', 'Timeout no rotation'\
                                                                            ,'Rotation', 'Timeout rotation'])

plt.xticks(fontsize = 'large')
plt.yticks(fontsize = 'large')
plt.xlabel('Instance', size = 15)
plt.ylabel('Execution time', size = 15)
plt.yscale('log')
plt.title('SMT execution time', size = 20) # CAMBIA QUI IL TITOLO DIOME
plt.legend(loc = 'upper left', fontsize='x-large')
plt.grid(True, which="minor")
threshold = 300
plt.axhline(threshold, color='red', ls='dotted')

if save_image:
    plt.savefig(name_image, edgecolor='w', facecolor = 'w')

plt.show()
