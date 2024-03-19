# Cornucopia

##### What is this?

Cornucopia is a small Eurorack power supply designed to pair with Doepfer busboards which have spade connectors for their power inputs. It is designed to be powered by an external AD-DC power brick, ideally at least 50W.

##### How much power does it provide?

In theory, Cornucopia can provide up to 2A +12v, 1A -12v, and 1A +5v. However, I haven't pushed mine nearly that far and really wanted the extra headroom for the off chance a single module was particularly power hungry.

##### Where does the design come from?

Cornucopia is a derivative work based on Winterbloom's Micronova. The differences between Micronova and Cornucopia:

- Increased potential power across all three Eurorack volages

- Spade connectors instead of a second Eurorack power header

- Pass-through power on the top and bottom of the board, making chaining together Cornucopia modules easier

- Moving some of the surface mount parts to accomodate the pass-through power

- Small silkscreen and footprint changes here and there

More details about Micronova are available at [Micronova - Winterbloom](https://winterbloom.com/shop/micronova).

##### Are there any rare/weird parts used?

The CUI DC-DC converters are the rarest parts. These must not be swapped for other DC-DC converters, especially in the -12v rail, as not all DC-DC converters support producing negative voltages.

Note that the DC-DC converters for +12 and -12v are flipped compared to Micronova to accomodate the converter's different, and slightly larger, footprint.

##### Are there any problems with the design?

With right-angled spade connectors, the screw holes on the right hand side are impossible to access. If you're building one for yourself, I'd recommend vertical spade connectors instead.

##### Do you have a BOM/Mouser cart/Tayda links?

Sorry, no. Things go out of stock so frequently it'd be a lot of work to keep these up to date. Other than the CUI DC-DC converters, everything in this project should be easy to source.

##### License and contributing

Cornucopia is open-source hardware. Please take a chance to review the [LICENSE](LICENSE.md) file.

![](images/cornucopia.png)
